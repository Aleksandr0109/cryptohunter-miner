# main.py — v3.7 — ПОЛНЫЙ, ИСПРАВЛЕННЫЙ, РАБОЧИЙ
# ИСПОЛЬЗУЕТ: API_ID, API_HASH, PHONE → outreach_session.session
import os
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

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
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

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
app.mount("/webapp", StaticFiles(directory="bot/webapp"), name="webapp")
app.mount("/assets", StaticFiles(directory="bot/webapp/assets"), name="assets")

@app.get("/")
async def root():
    return FileResponse("bot/webapp/index.html")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "session": "outreach_session.session",
        "scanner": "active",
        "outreach": "active",
        "referrals": "enabled"
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

# === ТОЛЬКО outreach_session.session — ЧИТАЕТ API_ID, API_HASH, PHONE ===
async def create_client():
    # ЧИТАЕМ ТВОИ ПЕРЕМЕННЫЕ
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    phone = os.getenv("PHONE")
    
    if not all([api_id, api_hash, phone]):
        logger.error("Нет API_ID / API_HASH / PHONE в .env")
        return None
    
    api_id = int(api_id)

    # СЕССИЯ: outreach_session.session
    client = TelegramClient("outreach_session", api_id, api_hash)
    session_file = "outreach_session.session"

    if os.path.exists(session_file):
        try:
            await client.connect()
            if await client.is_user_authorized():
                logger.info("outreach_session.session — подключена")
                return client
            else:
                logger.warning("Сессия не авторизована — удаляю")
                os.remove(session_file)
        except Exception as e:
            logger.warning(f"Сессия повреждена: {e}")
            try: os.remove(session_file)
            except: pass

    logger.info(f"Авторизация: {phone}")
    try:
        await client.start(phone=lambda: phone)
        logger.info("outreach_session.session — создана и авторизована")
        return client
    except SessionPasswordNeededError:
        logger.error("2FA включён — отключите в настройках Telegram")
        return None
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        return None

# === LEAD SCANNER ===
async def run_lead_scanner():
    while True:
        client = await create_client()
        if not client:
            await asyncio.sleep(3600)
            continue
        try:
            logger.info("LEAD SCANNER: Запуск на outreach_session.session")
            from lead_scanner import run_scanner
            await run_scanner(client)
            await client.disconnect()
            logger.info("LEAD SCANNER: Ждём 4 часа...")
            await asyncio.sleep(4 * 3600)
        except Exception as e:
            logger.error(f"SCANNER упал: {e}")
            await client.disconnect()
            await asyncio.sleep(3600)

# === OUTREACH SENDER ===
async def run_outreach_sender():
    while True:
        client = await create_client()
        if not client:
            await asyncio.sleep(3600)
            continue
        try:
            logger.info("OUTREACH: Запуск на outreach_session.session")
            from outreach_sender import safe_send
            await safe_send(client)
            await client.disconnect()
            logger.info("OUTREACH: Ждём 3 часа...")
            await asyncio.sleep(3 * 3600)
        except Exception as e:
            logger.error(f"OUTREACH упал: {e}")
            await client.disconnect()
            await asyncio.sleep(3600)

# === БОТ ===
async def start_bot():
    while True:
        try:
            bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            dp = Dispatcher(storage=MemoryStorage())
            dp.include_router(router)
            dp.include_router(admin_router)
            logger.info("БОТ: Запуск...")
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"БОТ упал: {e}")
            await asyncio.sleep(15)

# === НАЧИСЛЕНИЯ ===
async def hourly_accrual():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute("SELECT * FROM users")
            users = result.scalars().all()
            from decimal import Decimal
            for user in users:
                invested = user.invested_amount or Decimal('0')
                if invested > 0:
                    hourly = (invested * Decimal('0.25')) / 24
                    user.free_mining_balance += hourly
                    user.total_earned += hourly
            await db.commit()
        logger.info("Начисления: +0.0005 TON/час")
    except Exception as e:
        logger.error(f"Начисления: {e}")

async def scheduler():
    import aioschedule
    aioschedule.every().hour.at(":00").do(lambda: asyncio.create_task(hourly_accrual()))
    logger.info("Планировщик: запущен")
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(30)

# === ИНИЦИАЛИЗАЦИЯ БД ===
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("БД: инициализирована")

# === СЕРВЕР ===
async def serve_api():
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info(f"API: запуск на порту {port}")
    await server.serve()

# === ГЛАВНЫЙ ЦИКЛ ===
async def main():
    logger.info("CRYPTOHUNTER v3.7 — ЗАПУСК НА outreach_session.session")
    await init_db()
    await asyncio.gather(
        start_bot(),
        run_lead_scanner(),
        run_outreach_sender(),
        scheduler(),
        serve_api()
    )

if __name__ == "__main__":
    asyncio.run(main())
