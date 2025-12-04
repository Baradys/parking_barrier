import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect


from app.db.database import get_db


class ConnectionManager:
    def __init__(self):
        # Словарь для хранения подключений по barrier_id
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, barrier_id: int):
        await websocket.accept()
        if barrier_id not in self.active_connections:
            self.active_connections[barrier_id] = set()
        self.active_connections[barrier_id].add(websocket)

    def disconnect(self, websocket: WebSocket, barrier_id: int):
        if barrier_id in self.active_connections:
            self.active_connections[barrier_id].discard(websocket)
            if not self.active_connections[barrier_id]:
                del self.active_connections[barrier_id]

    async def send_to_barrier_clients(self, message: str, barrier_id: int):
        """Отправить сообщение всем клиентам, подписанным на определенный барьер"""
        if barrier_id in self.active_connections:
            dead_connections = set()
            for connection in self.active_connections[barrier_id].copy():
                try:
                    await connection.send_text(message)
                except:
                    dead_connections.add(connection)

            # Убираем мертвые соединения
            for dead_conn in dead_connections:
                self.active_connections[barrier_id].discard(dead_conn)

    async def broadcast_to_all(self, message: str):
        """Отправить сообщение всем подключенным клиентам"""
        for barrier_connections in self.active_connections.values():
            dead_connections = set()
            for connection in barrier_connections.copy():
                try:
                    await connection.send_text(message)
                except:
                    dead_connections.add(connection)

            # Убираем мертвые соединения
            for dead_conn in dead_connections:
                barrier_connections.discard(dead_conn)


manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, barrier_id: int):
    from app.db.barrier.requests import get_barrier_info
    await manager.connect(websocket, barrier_id)

    try:
        # Отправляем текущее состояние парковки при подключении
        db = next(get_db())
        try:
            barrier_info = await get_barrier_info(db, barrier_id)
            initial_data = {
                "type": "initial_data",
                "barrier_id": barrier_id,
                "park_amount": barrier_info.park_amount,
                "total_amount": barrier_info.total_amount,
                "city": barrier_info.city,
                "location": barrier_info.location
            }
            await websocket.send_text(json.dumps(initial_data))
        finally:
            await db.close()

        # Слушаем сообщения от клиента (опционально)
        while True:
            data = await websocket.receive_text()
            # Можно обрабатывать сообщения от клиента, если необходимо
            print(f"Received message from client: {data}")

    except WebSocketDisconnect:
        manager.disconnect(websocket, barrier_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, barrier_id)


async def notify_park_amount_change(barrier_id: int, new_park_amount: int, total_amount: int, city: str, location: str):
    """Функция для уведомления клиентов об изменении количества свободных мест"""
    message = {
        "type": "park_amount_update",
        "barrier_id": barrier_id,
        "park_amount": new_park_amount,
        "total_amount": total_amount,
        "city": city,
        "location": location,
        "occupied_amount": total_amount - new_park_amount,
        "timestamp": asyncio.get_event_loop().time()
    }

    await manager.send_to_barrier_clients(json.dumps(message), barrier_id)