# bot/handlers.py — v4.0: ТОЛЬКО /start + /admin
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from core.models import User, Referral
from core.database import AsyncSessionLocal
from bot.keyboard import main_menu
from sqlalchemy import select
from decimal import Decimal
import asyncio

router = Router()

# === /start + РЕФЕРАЛКА ===
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    args = message.text.split()
    payload = args[1] if len(args) > 1 else None

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()

        is_new = False
        if not user:
            is_new = True
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                referrer_id=int(payload) if payload and payload.isdigit() else None
            )
            db.add(user)

        if payload and payload.isdigit() and is_new:
            referrer_id = int(payload)
            referrer_result = await db.execute(select(User).where(User.user_id == referrer_id))
            referrer = referrer_result.scalar_one_or_none()

            if referrer and referrer.user_id != user.user_id:
                referral = Referral(
                    referrer_id=referrer_id,
                    referred_id=user.user_id,
                    level=1,
                    bonus_paid=Decimal('0')
                )
                db.add(referral)
                referrer.referral_count += 1
                await db.commit()
                await message.answer("Вы зарегистрированы по реферальной ссылке!")

        await db.commit()

        await message.answer(
            "Добро пожаловать в *CryptoHunter Miner*!\n"
            "25%/мес + бесплатный майнинг\n\n"
            "Нажмите кнопку ниже, чтобы открыть майнер:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

        # Убрано: напоминание через час
        # await asyncio.sleep(3600)
        # await message.answer("Посчитай доход с 200 TON: /calculator")


# === АДМИНКА (ОСТАЁТСЯ В ЧАТЕ) ===
@router.message(Command("admin"))
async def admin_panel(message: Message):
    ADMIN_ID = 123456789  # ← ЗАМЕНИ НА СВОЙ
    if message.from_user.id != ADMIN_ID:
        return await message.answer("Доступ запрещён.")

    await message.answer(
        "Админ-панель:\n"
        "/stats — статистика\n"
        "/broadcast — рассылка\n"
        "/leads — лиды",
        reply_markup=main_menu()  # или отдельная админская клавиатура
    )