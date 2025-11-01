# core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import AsyncGenerator
from config import DATABASE_URL

# Создаем движок с настройками для MySQL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Включаем логирование SQL запросов для отладки
    future=True,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Создаем фабрику сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генератор сессий для зависимостей"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()