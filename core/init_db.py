# core/init_db.py
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from core.database import engine
from core.models import Base

async def init_db():
    print("Удаляем старые таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Создаем новые таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("База данных успешно создана!")
    print("\nСозданы таблицы:")
    print("  - users")
    print("  - leads")
    print("  - transactions")
    print("  - referrals")
    
    print("\nСтруктура таблицы leads:")
    print("  - user_id (BigInteger)")
    print("  - source_channel (String)")
    print("  - source_type (String) — predefined | discovered | global_search")  # ← добавлено
    print("  - found_date (TIMESTAMP)")
    print("  - interest_keywords (Text) — JSON")
    print("  - contact_attempts (Integer)")
    print("  - conversion_status (String)")
    print("  - interest_score (Integer)")
    print("  - last_contact (TIMESTAMP)")
    print("  - notes (Text)")

    print("\nГотово! Запусти: python lead_scanner.py")

if __name__ == "__main__":
    asyncio.run(init_db())