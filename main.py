# main.py — v1.5 — ПООЧЕРЕДНЫЙ ЗАПУСК 4+4 ЧАСА
import os
import asyncio
import logging
import sys
from pathlib import Path

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

from config import BOT_TOKEN, TONKEEPER_API_KEY
from bot.handlers import router
from bot.admin import router as admin_router
from bot.outreach import start_outreach

import aiohttp
from sqlalchemy import select
from core.database import AsyncSessionLocal, engine
from core.models import Base, User, Referral, Transaction
from core.calculator import ProfitCalculator
from core.tonkeeper import TonkeeperAPI

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

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
tonkeeper = TonkeeperAPI()

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

# === API: QR Депозит ===
@app.post("/api/qr")
async def api_qr(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    amount = float(data.get("amount", 0))
    if amount < 1:
        raise HTTPException(400, "Min 1 TON")
    try:
        import qrcode
        import base64
        from io import BytesIO
        from decimal import Decimal
        
        address = await tonkeeper.get_address()
        url = f"ton://{address}?amount={int(amount * 1e9)}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode()

        async with AsyncSessionLocal() as db:
            user = await db.get(User, user_id)
            if user:
                user.pending_deposit = Decimal(str(amount))
                user.pending_address = address
                await db.commit()

        return JSONResponse({
            "url": url,
            "address": address,
            "qr_code": f"data:image/png;base64,{qr_base64}"
        })
    except Exception as e:
        logger.error(f"QR error: {e}")
        raise HTTPException(500, "QR generation failed")

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

# === API: Проверка платежа ===
@app.post("/api/check")
async def api_check(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user or not user.pending_address:
            return {"status": "no_pending"}

        address = user.pending_address
        amount = float(user.pending_deposit)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://toncenter.com/api/v3/transactions?address={address}&limit=10",
                headers={"X-API-Key": TONKEEPER_API_KEY}
            ) as resp:
                result = await resp.json()

        for tx in result.get("transactions", []):
            value = tx.get("in_msg", {}).get("value", 0)
            if value and int(value) >= int(amount * 1e9):
                from decimal import Decimal
                bonus = amount * 0.05
                user.invested_amount += Decimal(str(amount))
                user.free_mining_balance += Decimal(str(bonus))
                user.total_earned += Decimal(str(bonus))
                user.pending_deposit = None
                user.pending_address = None
                db.add(Transaction(
                    user_id=user.user_id,
                    type="deposit",
                    amount=Decimal(str(amount)),
                    tx_hash=tx["hash"],
                    status="success"
                ))
                await db.commit()
                return {"status": "success", "bonus": float(bonus)}
        return {"status": "pending"}

# === API: Рефералка ===
@app.post("/api/referral")
async def api_referral(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404)
        link = f"https://t.me/CryptoHunterTonBot?start={user.user_id}"
        direct_result = await db.execute(select(Referral).where(Referral.referrer_id == user.user_id, Referral.level == 1))
        direct = direct_result.scalars().all()
        level2_count = 0
        from decimal import Decimal
        total_income = Decimal('0')
        for ref in direct:
            l2 = await db.execute(select(Referral).where(Referral.referrer_id == ref.referred_id, Referral.level == 2))
            level2_count += l2.scalars().count()
            total_income += ref.bonus_paid
        return {
            "link": link,
            "direct_count": len(direct),
            "level2_count": level2_count,
            "income": float(total_income)
        }

# === Ежедневные начисления ===
async def daily_accrual():
    try:
        async with AsyncSessionLocal() as db:
            users = (await db.execute(select(User))).scalars().all()
            for user in users:
                from decimal import Decimal
                invested = user.invested_amount or Decimal('0')
                daily = ProfitCalculator.total_daily_income(invested)
                user.free_mining_balance += daily
                user.total_earned += daily
                user.mining_speed = ProfitCalculator.mining_speed(invested)
            await db.commit()
            logger.info("✅ Ежедневные начисления выполнены")
    except Exception as e:
        logger.error(f"❌ Ошибка начислений: {e}")

# === Планировщик ===
async def scheduler():
    import aioschedule
    aioschedule.every().day.at("00:00").do(lambda: asyncio.create_task(daily_accrual()))
    while True:
        await aioschedule.run_pending()
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
        
        # Используем сессию
        client = TelegramClient("scanner_session", API_ID, API_HASH)
        
        await client.start()
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
        
        from outreach_sender import safe_send
        await safe_send()
        
        logger.info("✅ Рассылка завершена")
        return True
        
    except Exception as e:
        logger.error(f"❌ Outreach Sender упал: {e}")
        return False

# === ОСНОВНОЙ ЦИКЛ ПООЧЕРЕДНОГО ЗАПУСКА ===
async def main_worker():
    """Главный рабочий цикл: 4 часа сканирование → 4 часа рассылка"""
    
    # Начинаем со сканирования
    current_service = "scanner"
    
    while True:
        try:
            if current_service == "scanner":
                logger.info("🔄 ЦИКЛ: Запускаем сканирование лидов")
                success = await run_lead_scanner()
                if success:
                    logger.info("⏰ Ждём 4 часа перед рассылкой...")
                    await asyncio.sleep(4 * 3600)  # 4 часа
                else:
                    logger.info("⏰ Ошибка сканирования, ждём 1 час...")
                    await asyncio.sleep(3600)  # 1 час при ошибке
                
                # Переключаем на рассылку
                current_service = "outreach"
                
            else:  # outreach
                logger.info("🔄 ЦИКЛ: Запускаем рассылку")
                success = await run_outreach_sender()
                if success:
                    logger.info("⏰ Ждём 4 часа перед сканированием...")
                    await asyncio.sleep(4 * 3600)  # 4 часа
                else:
                    logger.info("⏰ Ошибка рассылки, ждём 1 час...")
                    await asyncio.sleep(3600)  # 1 час при ошибке
                
                # Переключаем на сканирование
                current_service = "scanner"
                
        except Exception as e:
            logger.error(f"💥 Критическая ошибка в главном цикле: {e}")
            await asyncio.sleep(3600)  # 1 час при критической ошибке

# === Главная функция ===
async def main():
    logger.info("🚀 ЗАПУСК CRYPTOHUNTER MINER v1.5 - ПООЧЕРЕДНЫЙ ЦИКЛ 4+4 ЧАСА")

    await create_tables()

    # Запуск фоновых сервисов
    asyncio.create_task(start_bot_background())      # Постоянно
    asyncio.create_task(scheduler())                 # По расписанию
    asyncio.create_task(start_outreach())            # Outreach из bot.outreach
    
    # Запуск главного рабочего цикла
    asyncio.create_task(main_worker())

    # Веб-сервер
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"🌐 ЗАПУСК СЕРВЕРА НА ПОРТУ {port}")

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
