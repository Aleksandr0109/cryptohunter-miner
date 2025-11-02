# core/database.py — v4.0: ЯВНЫЙ ДРАЙВЕР aiomysql
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# === RAILWAY ДОБАВЛЯЕТ MYSQL_URL ===
DATABASE_URL = os.getenv("MYSQL_URL")

if not DATABASE_URL:
    raise ValueError("MYSQL_URL not found! Check Railway Variables.")

# === ДОБАВЛЯЕМ +aiomysql ===
DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://")

# === ДВИЖОК ===
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
