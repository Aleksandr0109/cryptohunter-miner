# main.py — v2.1 — ФИКС СЕССИЙ TELEGRAM
import os
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

# УСТАНОВКА EVENT LOOP
import uvloop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Добавляем корень проекта в путь
sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# === CONFIG ===
from config import BOT_TOKEN, BOT_USERNAME, TONKEEPER_API_KEY

from bot.handlers import router
from bot.admin import router as admin_router
from bot.outreach import start_outreach

import aiohttp
from sqlalchemy import select
from core.database import AsyncSessionLocal, engine
from core.models import Base, User, Referral, Transaction, PendingDeposit
from core.calculator import ProfitCalculator
from core.tonkeeper import tonkeeper

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# === БЕЗОПАСНОЕ СОЗДАНИЕ TELEGRAM КЛИЕНТОВ ===
async def create_safe_telethon_client(session_name, api_id, api_hash, phone=None):
    """Безопасное создание Telethon клиента с обработкой ошибок сессии"""
    session_file = f"{session_name}.session"
    
    # Если сессия существует и есть ошибка авторизации - удаляем её
    if os.path.exists(session_file):
        try:
            # Пробуем подключиться с существующей сессией
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()
            
            # Проверяем валидность сессии
            if not await client.is_user_authorized():
                raise Exception("Session not authorized")
                
            logger.info(f"✅ Используем существующую сессию: {session_name}")
            return client
            
        except Exception as e:
            logger.warning(f"❌ Ошибка сессии {session_name}: {e}. Удаляем и создаем новую...")
            try:
                await client.disconnect()
            except:
                pass
            if os.path.exists(session_file):
                os.remove(session_file)
    
    # Создаем новую сессию
    logger.info(f"🆕 Создаем новую сессию: {session_name}")
    client = TelegramClient(session_name, api_id, api_hash)
    
    if phone:
        await client.start(phone=phone)
    else:
        await client.start()
        
    return client

# === FastAPI ===
app = FastAPI(title="CryptoHunter Miner")

# === CORS + Telegram WebView ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def allow_telegram_webview(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "").lower()
    if any(x in user_agent for x in ["telegram", "iphone", "android", "mobile", "webview"]):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "ALLOWALL"
        response.headers["Content-Security-Policy"] = "frame-ancestors *;"
        return response
    return await call_next(request)

# === Tonkeeper ===
try:
    if hasattr(tonkeeper, 'wallet') and tonkeeper.wallet:
        logger.info(f"✅ TonkeeperAPI инициализирован: {tonkeeper.wallet.address.to_string()}")
    else:
        logger.warning("❌ Tonkeeper кошелек не инициализирован - проверь TONKEEPER_MNEMONIC")
except Exception as e:
    logger.error(f"Ошибка проверки Tonkeeper: {e}")

# === Статические файлы ===
app.mount("/webapp", StaticFiles(directory="bot/webapp"), name="webapp")
app.mount("/assets", StaticFiles(directory="bot/webapp/assets"), name="assets")

# === Основные маршруты ===
@app.get("/")
async def root():
    return FileResponse("bot/webapp/index.html")

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "CryptoHunter Miner API"}

@app.get("/style.css")
async def read_css():
    return FileResponse("bot/webapp/style.css", media_type="text/css")

@app.get("/script.js")
async def read_js():
    return FileResponse("bot/webapp/script.js", media_type="application/javascript")

@app.get("/favicon.ico")
async def read_favicon():
    return Response(content=b"", media_type="image/x-icon")

@app.get("/webapp/assets/{filename}")
async def serve_webapp_assets(filename: str):
    return FileResponse(f"bot/webapp/assets/{filename}")

# === SPA Fallback ===
@app.get("/{path:path}")
async def spa_fallback(path: str):
    if path.startswith('api/') or path.startswith('webapp/') or path.startswith('assets/'):
        raise HTTPException(status_code=404)
    return FileResponse("bot/webapp/index.html")

# === Валидация initData ===
def validate_init_data(init_data: str) -> dict | None:
    if not init_data:
        return None
    try:
        import urllib.parse
        import json
        params = dict([x.split('=', 1) for x in init_data.split('&')])
        user_str = urllib.parse.unquote(params.get('user', ''))
        user_data = json.loads(user_str)
        return {"user_id": int(user_data["id"]), "username": user_data.get("username")}
    except Exception as e:
        logger.error(f"initData error: {e}")
        return None

# === API: Пользователь ===
@app.post("/api/user")
async def api_user(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            from decimal import Decimal
            user = User(
                user_id=user_id,
                username=user_info.get("username", "test_user") if user_info else "test_user",
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
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
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

# === API: Создание депозита ===
@app.post("/api/deposit")
async def api_deposit(data: dict, request: Request):
    """Создание депозита с уникальным комментарием"""
    try:
        user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
        user_id = user_info["user_id"] if user_info else 8089114323
        
        amount = float(data.get("amount", 0))
        if amount < 1:
            raise HTTPException(400, "Минимум 1 TON")

        # Создаем платежный запрос
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
    """Проверка статуса платежа"""
    try:
        user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
        user_id = user_info["user_id"] if user_info else 8089114323
        
        deposit_id = data.get("deposit_id")
        
        status = await tonkeeper.check_payment_status(user_id, deposit_id)
        
        if status["status"] == "completed":
            # Зачисляем средства пользователю
            async with AsyncSessionLocal() as db:
                user = await db.get(User, user_id)
                if user:
                    from decimal import Decimal
                    amount = Decimal(str(status["amount"]))
                    bonus = amount * Decimal('0.05')
                    
                    # Обновляем балансы
                    user.invested_amount += amount
                    user.free_mining_balance += bonus
                    user.total_earned += bonus
                    
                    # Очищаем pending поля
                    user.pending_deposit = None
                    user.pending_address = None
                    
                    # Создаем транзакцию
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
        return {"status": "error", "message": "Ошибка проверки платежа"}

# === API: Вывод ===
@app.post("/api/withdraw")
async def api_withdraw(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    address = data["address"]
    from decimal import Decimal
    amount = Decimal(str(data.get("amount", 0)))
    if not address.startswith("kQ"):
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

# === API: Рефералка ===
@app.post("/api/referral")
async def api_referral(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = None

    if user_info and "user_id" in user_info:
        user_id = int(user_info["user_id"])
    else:
        user_id = 8089114323

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)

        if not user:
            from decimal import Decimal
            user = User(
                user_id=user_id,
                username=(user_info.get("username") if user_info else "anon"),
                invested_amount=Decimal('0'),
                free_mining_balance=Decimal('15.5'),
                total_earned=Decimal('0')
            )
            db.add(user)
            await db.flush()
            await db.commit()

        bot_username = BOT_USERNAME.lstrip('@') if BOT_USERNAME else "unknown_bot"
        link = f"https://t.me/{bot_username}?start=ref_{user.user_id}"

        from decimal import Decimal
        direct_result = await db.execute(
            select(Referral).where(Referral.referrer_id == user.user_id, Referral.level == 1)
        )
        direct = direct_result.scalars().all()

        level2_count = 0
        total_income = Decimal('0')

        for ref in direct:
            l2 = await db.execute(
                select(Referral).where(Referral.referrer_id == ref.referred_id, Referral.level == 2)
            )
            level2_count += len(l2.scalars().all())
            total_income += ref.bonus_paid or Decimal('0')

        return {
            "link": link,
            "direct_count": len(direct),
            "level2_count": level2_count,
            "income": float(total_income)
        }

# === ЕЖЕЧАСНЫЕ начисления ===
async def hourly_accrual():
    """Начисления каждый час"""
    try:
        async with AsyncSessionLocal() as db:
            users = (await db.execute(select(User))).scalars().all()
            total_accrued = 0
            users_count = 0

            for user in users:
                from decimal import Decimal
                invested = user.invested_amount or Decimal('0')

                if invested > 0:
                    hourly = ProfitCalculator.total_daily_income(invested) / 24
                    if hourly > 0:
                        user.free_mining_balance += hourly
                        user.total_earned += hourly
                        total_accrued += float(hourly)
                        users_count += 1

            await db.commit()

            if users_count > 0:
                logger.info(f"✅ Ежечасные начисления: {users_count} пользователей, {total_accrued:.6f} TON")
            else:
                logger.info("ℹ️ Нет пользователей с инвестициями для начислений")

    except Exception as e:
        logger.error(f"❌ Ошибка ежечасных начислений: {e}")

# === ЕЖЕДНЕВНЫЕ начисления (бонусные) ===
async def daily_accrual():
    """Дополнительные ежедневные начисления"""
    try:
        async with AsyncSessionLocal() as db:
            users = (await db.execute(select(User))).scalars().all()
            total_accrued = 0
            users_count = 0

            for user in users:
                from decimal import Decimal
                invested = user.invested_amount or Decimal('0')

                if invested > 0:
                    daily_bonus = invested * Decimal('0.01')
                    user.free_mining_balance += daily_bonus
                    user.total_earned += daily_bonus
                    total_accrued += float(daily_bonus)
                    users_count += 1

            await db.commit()

            if users_count > 0:
                logger.info(f"🎁 Ежедневные бонусы: {users_count} пользователей, {total_accrued:.6f} TON")
            else:
                logger.info("ℹ️ Нет пользователей для ежедневных бонусов")

    except Exception as e:
        logger.error(f"❌ Ошибка ежедневных начислений: {e}")

# === Планировщик ===
async def scheduler():
    """Улучшенный планировщик с ежечасными и ежедневными начислениями"""
    import aioschedule

    aioschedule.every().hour.at(":00").do(lambda: asyncio.create_task(hourly_accrual()))
    aioschedule.every().day.at("00:00").do(lambda: asyncio.create_task(daily_accrual()))

    logger.info("⏰ Планировщик запущен: ежечасные и ежедневные начисления")

    while True:
        try:
            await aioschedule.run_pending()
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"❌ Ошибка планировщика: {e}")
            await asyncio.sleep(60)

# === Создание таблиц ===
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ ТАБЛИЦЫ БД СОЗДАНЫ")

# === Бот в фоне ===
async def start_bot_background():
    while True:
        try:
            logger.info("🤖 ЗАПУСК ОСНОВНОГО БОТА...")
            bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
            dp = Dispatcher(storage=MemoryStorage())
            dp.include_router(router)
            dp.include_router(admin_router)
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"❌ Ошибка бота: {e}")
            await asyncio.sleep(15)

# === Lead Scanner ===
async def run_lead_scanner():
    """Запуск сканера лидов"""
    try:
        logger.info("🔍 ЗАПУСК LEAD SCANNER...")

        from telethon import TelegramClient
        from lead_scanner import run_scanner

        API_ID = int(os.getenv("API_ID"))
        API_HASH = os.getenv("API_HASH")
        PHONE = os.getenv("PHONE")

        # Используем безопасное создание клиента
        client = await create_safe_telethon_client("scanner_session", API_ID, API_HASH, PHONE)
        await run_scanner(client)
        await client.disconnect()

        logger.info("✅ Сканирование завершено")
        return True

    except Exception as e:
        logger.error(f"❌ Lead Scanner упал: {e}")
        return False

# === Outreach Sender ===
async def run_outreach_sender():
    """Запуск рассылки"""
    try:
        logger.info("📨 ЗАПУСК OUTREACH SENDER...")

        from telethon import TelegramClient
        from outreach_sender import safe_send

        API_ID = int(os.getenv("API_ID"))
        API_HASH = os.getenv("API_HASH")

        # Используем безопасное создание клиента
        client = await create_safe_telethon_client("scanner_session", API_ID, API_HASH)
        await safe_send(client)  # передаем клиент как аргумент
        await client.disconnect()

        logger.info("✅ Рассылка завершена")
        return True

    except Exception as e:
        logger.error(f"❌ Outreach Sender упал: {e}")
        return False

# === ОСНОВНОЙ ЦИКЛ: РАССЫЛКА ПЕРВАЯ → СКАНИРОВАНИЕ ===
async def main_worker():
    current_service = "outreach"

    while True:
        try:
            if current_service == "outreach":
                logger.info("🔄 ЦИКЛ: Запускаем РАССЫЛКУ")
                success = await run_outreach_sender()
                if success:
                    logger.info("⏰ Ждём 4 часа перед сканированием...")
                    await asyncio.sleep(4 * 3600)
                else:
                    logger.info("⏰ Ошибка рассылки, ждём 1 час...")
                    await asyncio.sleep(3600)

                current_service = "scanner"

            else:
                logger.info("🔄 ЦИКЛ: Запускаем СКАНИРОВАНИЕ")
                success = await run_lead_scanner()
                if success:
                    logger.info("⏰ Ждём 4 часа перед рассылкой...")
                    await asyncio.sleep(4 * 3600)
                else:
                    logger.info("⏰ Ошибка сканирования, ждём 1 час...")
                    await asyncio.sleep(3600)

                current_service = "outreach"

        except Exception as e:
            logger.error(f"💥 Критическая ошибка в главном цикле: {e}")
            await asyncio.sleep(3600)

# === Главная функция ===
async def main():
    logger.info("🚀 ЗАПУСК CRYPTOHUNTER MINER v2.1 - ФИКС СЕССИЙ TELEGRAM")

    await create_tables()

    asyncio.create_task(start_bot_background())
    asyncio.create_task(scheduler())
    asyncio.create_task(main_worker())

    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🌐 ЗАПУСК СЕРВЕРА НА ПОРТУ {port}")

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
