# main.py — v1.1: БОТ + MINI APP + API + СТАТИКА
import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, TONKEEPER_API_KEY
from bot.handlers import router
from bot.admin import router as admin_router
from bot.outreach import start_outreach

# === FastAPI + СТАТИКА ===
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import hmac
import hashlib
import urllib.parse
from decimal import Decimal
import aiohttp

# === БД + МОДЕЛИ ===
from core.database import AsyncSessionLocal
from core.models import User, Referral, Transaction
from core.calculator import ProfitCalculator
from core.tonkeeper import TonkeeperAPI
from sqlalchemy import select

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# === FastAPI ===
app = FastAPI()

# === СТАТИКА: Mini App ===
app.mount("/webapp", StaticFiles(directory="bot/webapp", html=True), name="webapp")

# === КОРЕНЬ → Mini App ===
@app.get("/")
async def root():
    return FileResponse("bot/webapp/index.html")

# === Tonkeeper ===
tonkeeper = TonkeeperAPI()

# === ВАЛИДАЦИЯ initData ===
def validate_init_data(init_data: str) -> dict | None:
    if not init_data:
        return None
    try:
        params = dict([x.split('=', 1) for x in init_data.split('&')])
        hash_ = params.pop('hash', '')
        data_check = '\n'.join(f"{k}={v}" for k, v in sorted(params.items()))
        secret = hashlib.sha256(f"WebAppData:{BOT_TOKEN}".encode()).digest()
        calculated = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated, hash_):
            return None
        user_str = params.get('user')
        if not user_str:
            return None
        user_data = eval(user_str)
        return {"user_id": int(user_data["id"]), "username": user_data.get("username")}
    except Exception as e:
        logger.error(f"initData error: {e}")
        return None


# === API: ПОЛЬЗОВАТЕЛЬ ===
@app.post("/api/user")
async def api_user(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    if not user_info:
        raise HTTPException(401, "Invalid initData")

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_info["user_id"])
        if not user:
            raise HTTPException(404, "User not found")

        return {
            "user_id": user.user_id,
            "balance": float(user.free_mining_balance),
            "invested": float(user.invested_amount),
            "earned": float(user.total_earned),
            "speed": round(ProfitCalculator.mining_speed(user.invested_amount) * 100, 2)
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
            "monthly": float(daily * 30),
            "yearly": float(daily * 365)
        }
    except:
        raise HTTPException(400, "Invalid amount")


# === API: QR ДЕПОЗИТ ===
@app.post("/api/qr")
async def api_qr(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    if not user_info:
        raise HTTPException(401)

    amount = float(data["amount"])
    if amount < 1:
        raise HTTPException(400, "Min 1 TON")

    address = await tonkeeper.get_address()
    url = f"ton://{address}?amount={amount}&testnet=true"

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_info["user_id"])
        if user:
            user.pending_deposit = Decimal(str(amount))
            user.pending_address = address
            await db.commit()

    return {"url": url}


# === API: ВЫВОД ===
@app.post("/api/withdraw")
async def api_withdraw(data: dict, request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    if not user_info:
        raise HTTPException(401)

    address = data["address"]
    if not address.startswith("kQ"):
        raise HTTPException(400, "Invalid address")

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_info["user_id"])
        if user.free_mining_balance < Decimal('1'):
            raise HTTPException(400, "Min 1 TON")

        amount = float(user.free_mining_balance)
        user.free_mining_balance = Decimal('0')
        db.add(Transaction(
            user_id=user.user_id,
            type="withdraw",
            amount=Decimal(str(amount)),
            status="pending"
        ))
        await db.commit()

    try:
        result = await tonkeeper.send_ton(address, amount)
        if result.get("ok"):
            tx_hash = result["result"]["hash"]
            async with AsyncSessionLocal() as db:
                tx = await db.execute(
                    select(Transaction).where(
                        Transaction.user_id == user.user_id,
                        Transaction.status == "pending"
                    ).order_by(Transaction.id.desc())
                )
                tx = tx.scalar_one()
                tx.tx_hash = tx_hash
                tx.status = "success"
                await db.commit()
            return {"message": f"Вывод {amount} TON отправлен!"}
        else:
            return {"message": "Ошибка сети"}
    except Exception as e:
        logger.error(f"Withdraw error: {e}")
        return {"message": "Ошибка сети"}


# === API: ПРОВЕРКА ПЛАТЕЖА ===
@app.post("/api/check")
async def api_check(request: Request):
    user_info = validate_init_data(request.headers.get("X-Telegram-WebApp-Init-Data"))
    if not user_info:
        raise HTTPException(401)

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_info["user_id"])
        if not user or not user.pending_address:
            return {"status": "no_pending"}

        address = user.pending_address
        amount = float(user.pending_deposit)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://testnet.toncenter.com/api/v3/transactions?address={address}&limit=10",
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
    if not user_info:
        raise HTTPException(401)

    async with AsyncSessionLocal() as db:
        user = await db.get(User, user_info["user_id"])
        if not user:
            raise HTTPException(404)

        link = f"https://t.me/cruptos023bot?start={user.user_id}"
        result = await db.execute(
            select(Referral).where(Referral.referrer_id == user.user_id, Referral.level == 1)
        )
        direct = result.scalars().all()

        level2_count = 0
        for ref in direct:
            res2 = await db.execute(
                select(Referral).where(Referral.referrer_id == ref.referred_id, Referral.level == 2)
            )
            level2_count += res2.scalars().count()

        total_income = sum(r.bonus_paid for r in direct)

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

            updated = 0
            for user in users:
                invested = user.invested_amount or Decimal('0')
                daily = ProfitCalculator.total_daily_income(invested)

                user.free_mining_balance += daily
                user.total_earned += daily
                user.mining_speed = ProfitCalculator.mining_speed(invested)
                updated += 1

            await db.commit()
            logger.info(f"Начислено {updated} пользователям")
    except Exception as e:
        logger.error(f"ОШИБКА НАЧИСЛЕНИЙ: {e}", exc_info=True)


# === ПЛАНИРОВЩИК ===
async def scheduler():
    import aioschedule
    aioschedule.every().day.at("00:00").do(
        lambda: asyncio.create_task(daily_accrual())
    )
    logger.info("Планировщик начислений запущен (00:00 UTC)")
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


# === ЗАПУСК ===
async def on_startup():
    logger.info("CryptoHunter Miner Bot v1.1 — ЗАПУЩЕН")
    asyncio.create_task(scheduler())
    asyncio.create_task(start_outreach())


# === ОСНОВНАЯ ФУНКЦИЯ ===
async def main():
    default = DefaultBotProperties(parse_mode=ParseMode.HTML)
    bot = Bot(token=BOT_TOKEN, default=default)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(admin_router)
    
    dp.startup.register(on_startup)

    # === ЗАПУСК БОТА + API ===
    import uvicorn
    config = uvicorn.Config(app, host="0.0.0.0", port=5000, log_level="info")
    server = uvicorn.Server(config)

    await asyncio.gather(
        dp.start_polling(bot),
        server.serve()
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную")