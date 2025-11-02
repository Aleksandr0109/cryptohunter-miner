# main.py — v0.8.0 FIXED STATIC FILES VERSION
import os
import asyncio
import logging
import sys
from pathlib import Path
import json
from decimal import Decimal
import urllib.parse
import qrcode
import base64
from io import BytesIO
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s'
)
logger = logging.getLogger(__name__)

# === FastAPI ===
app = FastAPI(title="CryptoHunter Miner")

# === CORS + TELEGRAM WEBVIEW FIX ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def allow_telegram_webview(request: Request, call_next):
    user_agent = request.headers.get("user-agent", "")
    if any(x in user_agent for x in ["Telegram", "iPhone", "Android", "Mobile", "WebView"]):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "ALLOWALL"
        response.headers["Content-Security-Policy"] = "frame-ancestors *;"
        return response
    return await call_next(request)

# === ИНИЦИАЛИЗАЦИЯ Tonkeeper ===
tonkeeper = TonkeeperAPI()

# === СТАТИКА ===
app.mount("/webapp", StaticFiles(directory="bot/webapp"), name="webapp")
app.mount("/assets", StaticFiles(directory="bot/webapp/assets"), name="assets")

# === ОСНОВНЫЕ МАРШРУТЫ ===
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

# === SPA FALLBACK ДЛЯ ВСЕХ ПУТЕЙ ===
@app.get("/{path:path}")
async def spa_fallback(path: str):
    """Обрабатывает все остальные пути для SPA"""
    # Игнорируем API пути
    if path.startswith('api/'):
        raise HTTPException(status_code=404, detail="API route not found")
    
    # Игнорируем статические файлы
    if path.startswith('webapp/') or path.startswith('assets/'):
        raise HTTPException(status_code=404, detail="Static file not found")
    
    # Для всех остальных путей возвращаем index.html
    return FileResponse("bot/webapp/index.html")

# === ВАЛИДАЦИЯ initData ===
def validate_init_data(init_data: str) -> dict | None:
    if not init_data:
        return None
    try:
        params = dict([x.split('=', 1) for x in init_data.split('&')])
        user_str = params.get('user', '')
        if not user_str:
            return None
        user_str = urllib.parse.unquote(user_str)
        user_data = json.loads(user_str)
        user_id = int(user_data["id"])
        return {"user_id": user_id, "username": user_data.get("username")}
    except Exception as e:
        logger.error(f"Ошибка валидации initData: {e}")
        return None

# === API: ПОЛЬЗОВАТЕЛЬ ===
@app.post("/api/user")
async def api_user(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
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

# === API: DASHBOARD ===
@app.post("/api/dashboard")
async def api_dashboard(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404, "User not found")
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

# === API: КАЛЬКУЛЯТОР ===
@app.post("/api/calc")
async def api_calc(data: dict):
    try:
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

# === API: QR ДЕПОЗИТ ===
@app.post("/api/qr")
async def api_qr(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    amount = float(data.get("amount", 0))
    if amount < 1:
        raise HTTPException(400, "Min 1 TON")
    try:
        address = await tonkeeper.get_address()
        url = f"ton://{address}?amount={int(amount * 1e9)}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
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
        logger.error(f"QR generation error: {e}")
        raise HTTPException(500, "QR generation failed")

# === API: ВЫВОД ===
@app.post("/api/withdraw")
async def api_withdraw(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    address = data["address"]
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
    return {"message": f"Вывод {float(amount)} TON отправлен на адрес {address}!"}

# === API: ПРОВЕРКА ПЛАТЕЖА ===
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

# === API: РЕФЕРАЛКА ===
@app.post("/api/referral")
async def api_referral(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    user_id = user_info["user_id"] if user_info else 8089114323
    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(404)
        link = f"https://t.me/CryptoHunterTonBot?start={user.user_id}"
        direct_result = await db.execute(
            select(Referral).where(Referral.referrer_id == user.user_id, Referral.level == 1)
        )
        direct = direct_result.scalars().all()
        level2_count = 0
        total_income = Decimal('0')
        for ref in direct:
            level2_result = await db.execute(
                select(Referral).where(Referral.referrer_id == ref.referred_id, Referral.level == 2)
            )
            level2_count += level2_result.scalars().count()
            total_income += ref.bonus_paid
        return {
            "link": link,
            "direct_count": len(direct),
            "level2_count": level2_count,
            "income": float(total_income)
        }

# === ЕЖЕДНЕВНЫЕ НАЧИСЛЕНИЯ ===
async def daily_accrual():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            for user in users:
                invested = user.invested_amount or Decimal('0')
                daily = ProfitCalculator.total_daily_income(invested)
                user.free_mining_balance += daily
                user.total_earned += daily
                user.mining_speed = ProfitCalculator.mining_speed(invested)
            await db.commit()
            logger.info("Ежедневные начисления выполнены")
    except Exception as e:
        logger.error(f"Ошибка начислений: {e}")

# === ПЛАНИРОВЩИК ===
async def scheduler():
    import aioschedule
    aioschedule.every().day.at("00:00").do(lambda: asyncio.create_task(daily_accrual()))
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(60)

# === АВТОСОЗДАНИЕ ТАБЛИЦ ===
async def create_tables():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ ТАБЛИЦЫ БАЗЫ ДАННЫХ СОЗДАНЫ")
    except Exception as e:
        logger.error(f"❌ Ошибка создания таблиц: {e}")

# === БОТ В ФОНОВОМ РЕЖИМЕ ===
async def start_bot_background():
    """Запуск бота как фоновой задачи"""
    try:
        logger.info("🤖 ЗАПУСК БОТА В ФОНОВОМ РЕЖИМЕ...")
        
        default = DefaultBotProperties(parse_mode=ParseMode.HTML)
        bot = Bot(token=BOT_TOKEN, default=default)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        dp.include_router(router)
        dp.include_router(admin_router)
        
        logger.info("✅ БОТ ЗАПУЩЕН (POLLING)")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"❌ Ошибка бота: {e}")
        await asyncio.sleep(30)
        asyncio.create_task(start_bot_background())

# === ГЛАВНАЯ ФУНКЦИЯ ===
async def main():
    """Основная функция запуска для Railway"""
    logger.info("🚀 ЗАПУСК CRYPTOHUNTER MINER НА RAILWAY...")
    
    # Создаем таблицы БД
    await create_tables()
    
    # Запускаем фоновые задачи
    asyncio.create_task(start_bot_background())
    asyncio.create_task(scheduler())
    asyncio.create_task(start_outreach())
    
    # Запускаем веб-сервер (ОСНОВНОЙ процесс для Railway)
    import uvicorn
    port = int(os.getenv("PORT", 5000))
    logger.info(f"🌐 ЗАПУСК ВЕБ-СЕРВЕРА НА ПОРТУ {port}")
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=port, 
        log_level="info",
        access_log=True
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
