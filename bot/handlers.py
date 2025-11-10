# bot/handlers.py — ФИНАЛЬНАЯ ВЕРСИЯ БЕЗ ТЕСТОВЫХ КОМАНД
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from core.models import User, Referral
from core.database import AsyncSessionLocal
from bot.keyboard import main_menu
from sqlalchemy import select
from decimal import Decimal
import asyncio
import re
import logging

logger = logging.getLogger(__name__)

router = Router()

def extract_referrer_id(payload: str) -> int | None:
    """Извлекает ID реферера из payload"""
    if not payload:
        return None
   
    if payload.startswith('ref_'):
        ref_id = payload[4:]
    elif payload.startswith('ref'):
        ref_id = payload[3:]
    else:
        ref_id = payload
   
    if ref_id.isdigit():
        return int(ref_id)
    return None

# === /start + РЕФЕРАЛКА ===
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    args = message.text.split()
    payload = args[1] if len(args) > 1 else None
    
    logger.info(f"🆕 /start от {message.from_user.id}, payload: {payload}")
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.user_id == message.from_user.id))
        user = result.scalar_one_or_none()
        is_new = False
        
        if not user:
            is_new = True
            user = User(
                user_id=message.from_user.id,
                username=message.from_user.username,
                referrer_id=extract_referrer_id(payload),
                # НАЧИНАЕМ С НУЛЯ
                invested_amount=Decimal('0'),
                free_mining_balance=Decimal('0'),
                total_earned=Decimal('0')
            )
            db.add(user)
            await db.commit()
            logger.info(f"✅ Создан новый пользователь: {message.from_user.id} с нулевым балансом")

        # Обработка рефералки
        if is_new and payload:
            referrer_id = extract_referrer_id(payload)
            if referrer_id and referrer_id != user.user_id:
                referrer_result = await db.execute(select(User).where(User.user_id == referrer_id))
                referrer = referrer_result.scalar_one_or_none()
                if referrer:
                    referral = Referral(
                        referrer_id=referrer_id,
                        referred_id=user.user_id,
                        level=1,
                        bonus_paid=Decimal('0')
                    )
                    db.add(referral)
                    referrer.referral_count += 1
                    await db.commit()
                    logger.info(f"🎯 Реферал зарегистрирован: {user.user_id} -> {referrer_id}")
                    await message.answer("Вы зарегистрированы по реферальной ссылке!")

        # Основное сообщение
        await message.answer(
            "Добро пожаловать в *CryptoHunter Miner*!\n"
            "25%/мес + бесплатный майнинг\n\n"
            "Нажмите кнопку ниже, чтобы открыть майнер:",
            reply_markup=main_menu(),
            parse_mode="Markdown"
        )

        # Запуск напоминаний только для новых пользователей
        if is_new:
            logger.info(f"⏰ Запуск напоминаний для {message.from_user.id}")
            asyncio.create_task(send_reminders(message.from_user.id, message.bot))
        else:
            logger.info(f"🔄 Существующий пользователь: {message.from_user.id}")

async def send_reminders(user_id: int, bot):
    """Отправка напоминаний пользователю"""
    try:
        logger.info(f"⏰ Напоминание 1 запланировано для {user_id}")
        
        # Первое напоминание через 1 час
        await asyncio.sleep(3600)  # 1 час
        
        try:
            await bot.send_message(
                user_id,
                "*Напомню о возможностях:*\n"
                "• Майнинг 25% в месяц\n"
                "• Рефералы: 5% с депозитов\n"
                "• Бесплатный доход каждый день\n\n"
                "Открыть майнер:",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
            logger.info(f"✅ Напоминание 1 отправлено для {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки напоминания 1 для {user_id}: {e}")
            return  # Если пользователь заблокировал бота, прекращаем рассылку

        # Второе напоминание через 2 часа после первого (3 часа от старта)
        await asyncio.sleep(7200)  # 2 часа
        
        try:
            await bot.send_message(
                user_id,
                "*Проверь свой баланс!*\n"
                "Ты уже мог заработать первые TON\n\n"
                "Открыть майнер и проверить:",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
            logger.info(f"✅ Напоминание 2 отправлено для {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки напоминания 2 для {user_id}: {e}")
            return

        # Третье напоминание через 21 час после второго (24 часа от старта)
        await asyncio.sleep(75600)  # 21 час
        
        try:
            await bot.send_message(
                user_id,
                "*Ежедневный бонус ждет!*\n"
                "Заходи каждый день для бесплатного майнинга\n\n"
                "Забрать бонус:",
                reply_markup=main_menu(),
                parse_mode="Markdown"
            )
            logger.info(f"✅ Напоминание 3 отправлено для {user_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки напоминания 3 для {user_id}: {e}")
            return
           
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в напоминаниях для {user_id}: {e}")
