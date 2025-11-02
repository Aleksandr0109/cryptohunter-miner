# core/init_db.py - ОБНОВЛЕННЫЙ СО ВСЕМИ ПОЛЯМИ
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
    
    print("\nСтруктура таблицы users:")
    print("  - user_id (BigInteger) - PRIMARY KEY")
    print("  - username (String)")
    print("  - first_seen (TIMESTAMP)")
    print("  - wallet_address (String)")
    print("  - invested_amount (DECIMAL) - инвестированные средства")
    print("  - free_mining_balance (DECIMAL) - баланс для вывода")
    print("  - total_earned (DECIMAL) - всего заработано")
    print("  - mining_speed (DECIMAL) - скорость майнинга")
    print("  - last_activity (TIMESTAMP)")
    print("  - referral_count (Integer) - количество рефералов")
    print("  - referrer_id (BigInteger) - ID пригласившего")
    print("  - status (String) - active/inactive")
    print("  - language (String)")
    print("  - notifications (Boolean)")
    print("  - pending_deposit (DECIMAL) - ожидающий депозит")
    print("  - pending_address (String) - адрес для депозита")
    
    print("\nСтруктура таблицы leads:")
    print("  - user_id (BigInteger)")
    print("  - source_channel (String)")
    print("  - source_type (String) — predefined | discovered | global_search")
    print("  - found_at (TIMESTAMP)")
    print("  - interest_keywords (Text) — JSON")
    print("  - contact_attempts (Integer)")
    print("  - conversion_status (String)")
    print("  - interest_score (Integer)")
    print("  - last_contact (TIMESTAMP)")
    print("  - notes (Text)")

    print("\nСтруктура таблицы transactions:")
    print("  - user_id (BigInteger)")
    print("  - type (String) - deposit/withdraw/bonus")
    print("  - amount (DECIMAL)")
    print("  - status (String) - pending/success/failed")
    print("  - created_at (TIMESTAMP)")
    print("  - completed_at (TIMESTAMP)")
    print("  - tx_hash (String) - хэш транзакции")
    print("  - notes (Text)")

    print("\nСтруктура таблицы referrals:")
    print("  - referrer_id (BigInteger) - кто пригласил")
    print("  - referred_id (BigInteger) - кого пригласили")
    print("  - level (Integer) - уровень реферала (1/2)")
    print("  - bonus_paid (DECIMAL) - выплаченный бонус")
    print("  - created_at (TIMESTAMP)")
    print("  - status (String) - active/inactive")

    print("\nГотово! База готова к работе с Mini-App.")

if __name__ == "__main__":
    asyncio.run(init_db())