# bot/handlers.py — v4.2: HTTPS + БЕРЁМ URL ИЗ .env (БЕЗ ДУБЛЕЙ)
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

# Список администраторов (замени на свои ID)
ADMIN_IDS = [8089114323, 123456789]  # Добавь свои ID администраторов

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

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

# === КОМАНДА ДЛЯ ТЕСТИРОВАНИЯ НАЧИСЛЕНИЙ ===
@router.message(Command("test_accrual"))
async def test_accrual(message: Message):
    """Тестовая команда для начисления за 1 час ВСЕМ пользователям"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Команда только для администраторов")
        return
    
    try:
        async with AsyncSessionLocal() as db:
            # Получаем всех пользователей
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            updated_count = 0
            total_accrued = Decimal('0')
            
            for user in users:
                # Даже если invested_amount = 0, начисляем базовый доход
                invested = user.invested_amount or Decimal('0')
                
                # Базовый почасовой доход (бесплатный майнинг)
                if invested > 0:
                    # Если есть инвестиции: 25% годовых
                    hourly = (invested * Decimal('0.25')) / Decimal('365') / Decimal('24')
                else:
                    # Если нет инвестиций: базовый бесплатный майнинг
                    hourly = Decimal('0.0005')  # 0.0005 TON/час
                
                user.free_mining_balance += hourly
                user.total_earned += hourly
                updated_count += 1
                total_accrued += hourly
                
                logger.info(f"💰 Тест: начислено {hourly:.6f} TON пользователю {user.user_id} (инвест: {invested})")
            
            await db.commit()
            
            await message.answer(
                f"✅ Тестовые начисления выполнены!\n"
                f"• Обработано пользователей: {updated_count}\n"
                f"• Общая сумма: {total_accrued:.6f} TON\n"
                f"• Среднее на пользователя: {total_accrued/updated_count if updated_count > 0 else 0:.6f} TON\n\n"
                f"Проверьте балансы в веб-приложении!"
            )
            logger.info(f"💰 Тест начислений: {updated_count} пользователей, {total_accrued:.6f} TON")
            
    except Exception as e:
        logger.error(f"❌ Ошибка тестовых начислений: {e}")
        await message.answer(f"❌ Ошибка: {e}")

# === КОМАНДА ДЛЯ ПРОСМОТРА ПОЛЬЗОВАТЕЛЕЙ ===
@router.message(Command("list_users"))
async def list_users(message: Message):
    """Показать всех пользователей"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Команда только для администраторов")
        return
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            if not users:
                await message.answer("📭 В базе нет пользователей")
                return
            
            response = "👥 Список пользователей:\n\n"
            for user in users:
                invested = user.invested_amount or Decimal('0')
                balance = user.free_mining_balance or Decimal('0')
                earned = user.total_earned or Decimal('0')
                
                response += f"ID: {user.user_id}\n"
                response += f"Username: @{user.username or 'нет'}\n"
                response += f"Инвест: {float(invested):.2f} TON\n"
                response += f"Баланс: {float(balance):.2f} TON\n"
                response += f"Заработано: {float(earned):.2f} TON\n"
                response += f"Рефералов: {user.referral_count}\n"
                response += "─" * 30 + "\n"
            
            # Если сообщение слишком длинное, разбиваем на части
            if len(response) > 4000:
                part1 = response[:4000]
                part2 = response[4000:]
                await message.answer(part1)
                await message.answer(part2)
            else:
                await message.answer(response)
                
    except Exception as e:
        logger.error(f"❌ Ошибка получения пользователей: {e}")
        await message.answer(f"❌ Ошибка: {e}")

# === КОМАНДА ДЛЯ ПРОВЕРКИ БАЛАНСОВ ===
@router.message(Command("check_balances"))
async def check_balances(message: Message):
    """Проверка балансов всех пользователей"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Команда только для администраторов")
        return
    
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User))
            users = result.scalars().all()
            
            response = "📊 Балансы пользователей:\n\n"
            total_invested = Decimal('0')
            total_balance = Decimal('0')
            total_earned = Decimal('0')
            
            for user in users:
                invested = user.invested_amount or Decimal('0')
                balance = user.free_mining_balance or Decimal('0')
                earned = user.total_earned or Decimal('0')
                
                total_invested += invested
                total_balance += balance
                total_earned += earned
                
                response += f"👤 {user.user_id}: инвест={float(invested):.2f}, баланс={float(balance):.2f}, заработано={float(earned):.2f}\n"
            
            response += f"\n📈 Итого:\n"
            response += f"• Инвестировано: {float(total_invested):.2f} TON\n"
            response += f"• Балансы: {float(total_balance):.2f} TON\n"
            response += f"• Заработано: {float(total_earned):.2f} TON\n"
            response += f"• Пользователей: {len(users)}"
            
            # Если сообщение слишком длинное, разбиваем на части
            if len(response) > 4000:
                part1 = response[:4000]
                part2 = response[4000:]
                await message.answer(part1)
                await message.answer(part2)
            else:
                await message.answer(response)
                
    except Exception as e:
        logger.error(f"❌ Ошибка проверки балансов: {e}")
        await message.answer(f"❌ Ошибка: {e}")

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

# Дополнительные обработчики для тестирования
@router.message(Command("test_reminder"))
async def test_reminder(message: Message):
    """Тестовая команда для проверки напоминаний"""
    logger.info(f"🧪 Тест напоминания для {message.from_user.id}")
    asyncio.create_task(send_reminders(message.from_user.id, message.bot))
    await message.answer("✅ Напоминания запущены! Проверяй через 1 час.")

@router.message(Command("status"))
async def status(message: Message):
    """Проверка статуса бота"""
    await message.answer(
        "🤖 Бот работает!\n"
        "• Напоминания: активны\n"
        "• Майнинг: 25%/мес\n"
        "• Рефералы: 5%\n\n"
        "Открыть майнер:",
        reply_markup=main_menu(),
        parse_mode="Markdown"
    )
