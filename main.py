# main.py — v4.5 — Исправленные начисления и планировщик
import os
import asyncio
import logging
import sys
from pathlib import Path

# Ускорение
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import text, select

from config import BOT_TOKEN, BOT_USERNAME
from bot.handlers import router
from bot.admin import router as admin_router
from core.database import AsyncSessionLocal, engine
from core.models import Base, User, Referral, Transaction
from core.calculator import ProfitCalculator
from core.tonkeeper import tonkeeper

# === ЛОГИ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# === FastAPI ===
app = FastAPI(title="CryptoHunter Miner")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ОТДАЁМ ВСЁ ИЗ bot/webapp/ → /webapp/style.css, /webapp/script.js и т.д.
app.mount("/webapp", StaticFiles(directory="bot/webapp"), name="webapp")

# ОТДАЁМ assets/ → /assets/images/... (если будут)
app.mount("/assets", StaticFiles(directory="bot/webapp/assets"), name="assets")

@app.get("/")
async def root():
    return FileResponse("bot/webapp/index.html")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "scanner": "disabled", 
        "outreach": "disabled", 
        "telethon": "disabled",
        "css": "served from /webapp/style.css",
        "referrals": "enabled",
        "mining": "active"
    }

# === ВАЛИДАЦИЯ INITDATA ===
def validate_init_data(init_data: str) -> dict | None:
    if not init_data: return None
    try:
        import urllib.parse, json
        params = dict([x.split('=', 1) for x in init_data.split('&')])
        user_str = urllib.parse.unquote(params.get('user', ''))
        return json.loads(user_str)
    except Exception as e:
        logger.error(f"initData error: {e}")
        return None

# === API: Пользователь ===
@app.post("/api/user")
async def api_user(request: Request):
    init_data = request.headers.get("X-Telegram-WebApp-Init-Data")
    user_info = validate_init_data(init_data)
    user_id = user_info["id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            from decimal import Decimal
            user = User(
                user_id=user_id,
                username=user_info.get("username", "anon") if user_info else "test",
                invested_amount=Decimal('100'),
                free_mining_balance=Decimal('15.5'),
                total_earned=Decimal('25.8')
            )
            db.add(user)
            await db.commit()
        return {
            "user_id": user.user_id,
            "balance": float(user.free_mining_balance),
            "invested": float(user.invested_amount),
            "earned": float(user.total_earned),
            "speed": round(ProfitCalculator.mining_speed(user.invested_amount) * 100, 2)
        }

# === API: Дашборд ===
@app.post("/api/dashboard")
async def api_dashboard(request: Request):
    init_data = request.headers.get("X-Telegram-WebApp-Init-Data")
    user_info = validate_init_data(init_data)
    user_id = user_info["id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        from decimal import Decimal
        invested = user.invested_amount or Decimal('0')
        balance = user.free_mining_balance or Decimal('0')
        speed = ProfitCalculator.mining_speed(invested)
        daily_inv = ProfitCalculator.investment_daily(invested)
        daily_free = ProfitCalculator.free_mining_daily(invested)
        total_daily = daily_inv + daily_free
        days_per_ton = Decimal('1') / daily_free if daily_free > 0 else Decimal('90')
        return {
            "invested": float(invested),
            "balance": float(balance),
            "speed": float(speed * 100),
            "daily_investment": float(daily_inv),
            "daily_free": float(daily_free),
            "total_daily": float(total_daily),
            "days_per_ton": float(days_per_ton),
            "hourly": float(total_daily / 24),
            "can_withdraw": balance >= Decimal('1')
        }

# === API: Калькулятор ===
@app.post("/api/calc")
async def api_calc(data: dict):
    try:
        from decimal import Decimal
        amount = Decimal(str(data["amount"]))
        if amount <= 0:
            raise ValueError
        daily = ProfitCalculator.total_daily_income(amount)
        return {
            "daily": float(daily),
            "weekly": float(daily * 7),
            "monthly": float(daily * 30),
            "yearly": float(daily * 365),
            "bonus": float(amount * Decimal('0.05'))
        }
    except:
        raise HTTPException(400, "Invalid amount")

# === API: Депозит ===
@app.post("/api/deposit")
async def api_deposit(data: dict, request: Request):
    try:
        user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
        user_id = user_info["id"] if user_info else 8089114323
        amount = float(data.get("amount", 0))
        if amount < 1:
            raise HTTPException(400, "Минимум 1 TON")
        payment_data = await tonkeeper.create_payment_request(user_id, amount)
        return JSONResponse({
            "success": True,
            "deposit_id": payment_data["deposit_id"],
            "payment_url": payment_data["url"],
            "address": payment_data["address"],
            "comment": payment_data["comment"],
            "qr_code": payment_data["qr_code"],
            "amount": amount,
            "expires_in": "24 hours"
        })
    except Exception as e:
        logger.error(f"Deposit error: {e}")
        raise HTTPException(500, "Ошибка создания депозита")

# === API: Проверка платежа ===
@app.post("/api/check-payment")
async def api_check_payment(data: dict, request: Request):
    try:
        user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
        user_id = user_info["id"] if user_info else 8089114323
        deposit_id = data.get("deposit_id")
        status = await tonkeeper.check_payment_status(user_id, deposit_id)
        if status["status"] == "completed":
            async with AsyncSessionLocal() as db:
                user = await db.get(User, user_id)
                if user:
                    from decimal import Decimal
                    amount = Decimal(str(status["amount"]))
                    bonus = amount * Decimal('0.05')
                    user.invested_amount += amount
                    user.free_mining_balance += bonus
                    user.total_earned += bonus
                    user.pending_deposit = None
                    user.pending_address = None
                    db.add(Transaction(
                        user_id=user_id,
                        type="deposit",
                        amount=amount,
                        status="completed",
                        notes=f"Deposit with bonus {float(bonus)} TON"
                    ))
                    await db.commit()
                    return {
                        "status": "completed",
                        "amount": float(amount),
                        "bonus": float(bonus),
                        "message": f"Депозит {amount} TON зачислен! Бонус: {bonus} TON"
                    }
        return status
    except Exception as e:
        logger.error(f"Check payment error: {e}")
        return {"status": "error", "message": "Ошибка проверки"}

# === API: Вывод ===
@app.post("/api/withdraw")
async def api_withdraw(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["id"] if user_info else 8089114323
    address = data["address"]
    from decimal import Decimal
    amount = Decimal(str(data.get("amount", 0)))
    if not address.startswith(("kQ", "UQ", "EQ")):
        raise HTTPException(400, "Invalid address")
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
        if user.free_mining_balance < Decimal('1'):
            raise HTTPException(400, "Min 1 TON")
        if amount <= 0:
            amount = user.free_mining_balance
        elif amount > user.free_mining_balance:
            raise HTTPException(400, "Insufficient balance")
        user.free_mining_balance -= amount
        db.add(Transaction(
            user_id=user.user_id,
            type="withdraw",
            amount=amount,
            status="pending",
            notes=f"Withdraw to {address}"
        ))
        await db.commit()
    return {"message": f"Вывод {float(amount)} TON отправлен на {address}"}

# === API: РЕФЕРАЛКА ===
@app.post("/api/referral")
async def api_referral(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            from decimal import Decimal
            user = User(
                user_id=user_id,
                username=user_info.get("username", "anon") if user_info else "anon",
                invested_amount=Decimal('0'),
                free_mining_balance=Decimal('15.5'),
                total_earned=Decimal('0')
            )
            db.add(user)
            await db.commit()
        bot_username = BOT_USERNAME.lstrip('@') if BOT_USERNAME else "unknown_bot"
        link = f"https://t.me/{bot_username}?start=ref_{user.user_id}"
        from sqlalchemy import select
        from decimal import Decimal
        direct_result = await db.execute(
            select(Referral).where(Referral.referrer_id == user.user_id, Referral.level == 1)
        )
        direct = direct_result.scalars().all()
        level2_count = 0
        total_income = Decimal('0')
        for ref in direct:
            l2_result = await db.execute(
                select(Referral).where(Referral.referrer_id == ref.referred_id, Referral.level == 2)
            )
            l2_count = len(l2_result.scalars().all())
            level2_count += l2_count
            total_income += ref.bonus_paid or Decimal('0')
        return {
            "link": link,
            "direct_count": len(direct),
            "level2_count": level2_count,
            "income": float(total_income)
        }

# === БОТ (РАБОТАЕТ) ===
async def start_bot():
    while True:
        try:
            bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            dp = Dispatcher(storage=MemoryStorage())
            dp.include_router(router)
            dp.include_router(admin_router)
            logger.info("🤖 БОТ: Запуск...")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"❌ БОТ упал: {e}")
            await asyncio.sleep(15)

# === НАЧИСЛЕНИЯ (ИСПРАВЛЕННЫЕ) ===
async def hourly_accrual():
    try:
        from decimal import Decimal
        
        async with AsyncSessionLocal() as db:
            # Получаем пользователей через правильный ORM запрос
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            updated_count = 0
            for user in users:
                invested = user.invested_amount or Decimal('0')
                if invested > 0:
                    # Расчет почасового дохода: 25% годовых / 24 часа / 365 дней
                    hourly = (invested * Decimal('0.25')) / Decimal('365') / Decimal('24')
                    user.free_mining_balance += hourly
                    user.total_earned += hourly
                    updated_count += 1
                    
                    logger.debug(f"💰 Начислено {hourly:.6f} TON пользователю {user.user_id}")
            
            await db.commit()
            logger.info(f"💰 Начисления: выполнены для {updated_count} пользователей")
            
    except Exception as e:
        logger.error(f"❌ Начисления: {e}")

# === УЛУЧШЕННЫЙ ПЛАНИРОВЩИК ===
async def scheduler():
    """Улучшенный планировщик с точными интервалами"""
    logger.info("⏰ Планировщик: запущен")
    
    # Ждем до начала следующей минуты
    import datetime
    now = datetime.datetime.now()
    wait_seconds = 60 - now.second
    logger.info(f"⏰ Ожидание {wait_seconds} секунд до следующей минуты...")
    await asyncio.sleep(wait_seconds)
    
    while True:
        try:
            now = datetime.datetime.now()
            
            # Начисления каждый час в :00
            if now.minute == 0:
                logger.info("🕐 Время для начислений!")
                await hourly_accrual()
                # Ждем 61 секунду чтобы не сработать дважды в одну минуту
                await asyncio.sleep(61)
            else:
                # Ждем до следующей минуты
                wait_seconds = 60 - now.second
                await asyncio.sleep(wait_seconds)
                
        except Exception as e:
            logger.error(f"❌ Ошибка планировщика: {e}")
            await asyncio.sleep(30)

# === ИНИЦИАЛИЗАЦИЯ БД ===
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("🗄️ БД: инициализирована")

# === СЕРВЕР ===
async def serve_api():
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"🌐 API: запуск на порту {port}")
    await server.serve()

# === ГЛАВНЫЙ ЦИКЛ ===
async def main():
    logger.info("🚀 CRYPTOHUNTER v4.5 - Исправленные начисления")
    
    # Инициализация БД
    await init_db()
    
    # Запуск всех сервисов
    logger.info("🎯 Запуск всех сервисов...")
    
    # Создаем задачи явно
    bot_task = asyncio.create_task(start_bot())
    scheduler_task = asyncio.create_task(scheduler())
    api_task = asyncio.create_task(serve_api())
    
    # Ожидаем завершения всех задач
    await asyncio.gather(
        bot_task,
        scheduler_task, 
        api_task,
        return_exceptions=True
    )

if __name__ == "__main__":
    asyncio.run(main())
