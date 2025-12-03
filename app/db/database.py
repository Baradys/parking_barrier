import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DB_USER = os.getenv("DB_USER", "barrier_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "barrier_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "barrier_db")

# ВАЖНО: async‑драйвер
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Создание async engine
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    echo=True,  # Отключите в production
)

# Async SessionLocal
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base класс для моделей
Base = declarative_base()


# Dependency для получения async‑сессии БД (FastAPI / ручное использование)
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
