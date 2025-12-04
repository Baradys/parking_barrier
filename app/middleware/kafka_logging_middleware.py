import json
import logging
import time
from typing import Callable, Awaitable

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send

# Если ставите aiokafka:
# pip install aiokafka
from aiokafka import AIOKafkaProducer

logger = logging.getLogger("kafka_logger")


class KafkaLoggingMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        bootstrap_servers: str,
        topic: str,
    ) -> None:
        self.app = app
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self._producer: AIOKafkaProducer | None = None

    async def _get_producer(self) -> AIOKafkaProducer:
        if self._producer is None:
            self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
            await self._producer.start()
        return self._producer

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            # Прокидываем не-HTTP (websocket, lifespan и т.п.)
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        start_time = time.monotonic()

        async def send_wrapper(message):
            # перехватываем ответ, чтобы узнать статус
            if message["type"] == "http.response.start":
                process_time = time.monotonic() - start_time
                client_host, client_port = (None, None)
                if scope.get("client"):
                    client_host, client_port = scope["client"]

                log_record = {
                    "method": request.method,
                    "path": request.url.path,
                    "query": str(request.url.query),
                    "client_host": client_host,
                    "client_port": client_port,
                    "status_code": message["status"],
                    "process_time_ms": round(process_time * 1000, 2),
                }

                # Лог в локальный логгер
                logger.info("HTTP %s %s -> %s (%sms)",
                            log_record["method"],
                            log_record["path"],
                            log_record["status_code"],
                            log_record["process_time_ms"])

                # Отправка в Kafka
                try:
                    producer = await self._get_producer()
                    await producer.send_and_wait(
                        self.topic,
                        json.dumps(log_record).encode("utf-8"),
                    )
                except Exception:
                    logger.exception("Failed to send log to Kafka")

            await send(message)

        await self.app(scope, receive, send_wrapper)

    async def close(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
