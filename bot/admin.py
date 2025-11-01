# bot/admin.py — АДМИН-ПАНЕЛЬ v1.2 + РАССЫЛКА ВСЕМ ПОЛЬЗОВАТЕЛЯМ
import asyncio
import csv
import logging
from datetime import datetime
from pathlib import Path

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from core.database import AsyncSessionLocal
from core.models import User, Lead, Transaction
from core.calculator import ProfitCalculator
from bot.outreach import start_outreach
from sqlalchemy import select, func
from decimal import Decimal

# === КОНФИГУРАЦИЯ ===
ADMIN_ID = 8089114323
logger = logging.getLogger(__name__)
router = Router()

# === FSM ===
class AdminStates(StatesGroup):
    waiting_for_broadcast = State()

# === КЛАВИАТУРА ===
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_keyboard():
    kb = [
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Рассылка ВСЕМ", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="💰 Начислить всем", callback_data="admin_accrue")],
        [InlineKeyboardButton(text="📁 Экспорт лидов", callback_data="admin_export")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

# === ВХОД ===
@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Доступ запрещён.")
        return
    await message.answer(
        "<b>🧩 Админ-панель CryptoHunter</b>\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )

# === СТАТИСТИКА ===
@router.callback_query(F.data == "admin_stats")
async def admin_stats(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    async with AsyncSessionLocal() as db:
        # Пользователи
        total_users = (await db.execute(select(func.count(User.user_id)))).scalar()
        active_users = (await db.execute(select(func.count(User.user_id)).where(User.status == 'active'))).scalar()
        
        # Лиды
        total_leads = (await db.execute(select(func.count(Lead.id)))).scalar()
        contacted = (await db.execute(select(func.count(Lead.id)).where(Lead.conversion_status != 'not_contacted'))).scalar()
        
        # Финансы
        total_invested = (await db.execute(select(func.sum(User.invested_amount)))).scalar() or Decimal('0')
        total_earned = (await db.execute(select(func.sum(User.total_earned)))).scalar() or Decimal('0')
        
        conversion = (contacted / total_leads * 100) if total_leads > 0 else 0

    text = (
        f"<b>📊 СТАТИСТИКА СИСТЕМЫ</b>\n\n"
        f"👥 <b>Пользователи:</b> <code>{total_users}</code> (активных: <code>{active_users}</code>)\n"
        f"🎯 <b>Лиды:</b> <code>{total_leads}</code> (обработано: <code>{contacted}</code>)\n"
        f"📈 <b>Конверсия:</b> <code>{conversion:.1f}%</code>\n\n"
        f"💰 <b>Инвестировано:</b> <code>{total_invested:.2f} TON</code>\n"
        f"💸 <b>Выплачено:</b> <code>{total_earned:.2f} TON</code>\n"
        f"📊 <b>Чистый доход:</b> <code>{(total_invested - total_earned):.2f} TON</code>"
    )
    await call.message.edit_text(text, reply_markup=get_admin_keyboard(), parse_mode="HTML")

# === РАССЫЛКА ВСЕМ ПОЛЬЗОВАТЕЛЯМ ===
@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != ADMIN_ID:
        return
    await call.message.edit_text(
        "Введите текст для рассылки ВСЕМ пользователям:\n"
        "<i>Отправьте сообщение — оно будет разослано всем пользователям бота</i>",
        parse_mode="HTML"
    )
    await state.set_state(AdminStates.waiting_for_broadcast)

@router.message(AdminStates.waiting_for_broadcast)
async def admin_broadcast_send(message: Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text or message.caption or "Привет!"
    
    async with AsyncSessionLocal() as db:
        # Получаем ВСЕХ пользователей из таблицы users
        result = await db.execute(select(User))
        users = result.scalars().all()
        
        sent = 0
        failed = 0
        
        # Отправляем прогресс
        progress_msg = await message.answer(f"🔄 Начинаем рассылку... 0/{len(users)}")
        
        for i, user in enumerate(users):
            try:
                await message.bot.send_message(user.user_id, text)
                sent += 1
                
                # Обновляем прогресс каждые 10 сообщений
                if i % 10 == 0:
                    await progress_msg.edit_text(
                        f"🔄 Рассылка... {i+1}/{len(users)}\n"
                        f"✅ Отправлено: {sent}\n"
                        f"❌ Ошибок: {failed}"
                    )
                
                await asyncio.sleep(0.05)  # Антифлуд
                
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение пользователю {user.user_id}: {e}")
                failed += 1
        
        await progress_msg.edit_text(
            f"✅ Рассылка завершена!\n"
            f"📤 Отправлено: {sent} пользователям\n"
            f"❌ Не удалось: {failed}\n"
            f"📊 Всего: {len(users)} пользователей"
        )
    
    await state.clear()

# === НАЧИСЛЕНИЯ ===
@router.callback_query(F.data == "admin_accrue")
async def admin_accrue(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    from core.calculator import ProfitCalculator
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
    await call.message.edit_text(
        f"💰 Начислено {updated} пользователям!",
        reply_markup=get_admin_keyboard()
    )

# === ЭКСПОРТ CSV С КЛЮЧЕВЫМИ СЛОВАМИ ===
@router.callback_query(F.data == "admin_export")
async def admin_export(call: CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        return
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Lead))
        leads = result.scalars().all()
    
    filename = f"leads_export_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.csv"
    filepath = Path("exports") / filename
    filepath.parent.mkdir(exist_ok=True)
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "ID", "User ID", "Username", "First Name", 
            "Источник", "Тип источника", "Статус", 
            "Попыток контакта", "Баллы интереса", "Ключевые слова",
            "Найден", "Последний контакт", "Заметки"
        ])
        for lead in leads:
            # Форматируем ключевые слова в читаемую строку
            keywords_str = ", ".join(lead.keywords_list) if lead.keywords_list else ""
            
            writer.writerow([
                lead.id,
                lead.user_id,
                lead.username or "",
                lead.first_name or "",
                lead.source_channel,
                lead.source_type,
                lead.conversion_status,
                lead.contact_attempts,
                lead.interest_score,
                keywords_str,
                lead.found_at.strftime("%Y-%m-%d %H:%M") if lead.found_at else "",
                lead.last_contact.strftime("%Y-%m-%d %H:%M") if lead.last_contact else "",
                lead.notes or ""
            ])
    
    await call.message.answer_document(
        FSInputFile(filepath),
        caption=f"📊 Экспорт лидов: {len(leads)} записей\n"
                f"⏰ Время выгрузки: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await call.message.edit_reply_markup(reply_markup=get_admin_keyboard())