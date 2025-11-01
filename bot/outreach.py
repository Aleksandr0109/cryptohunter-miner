# bot/outreach.py
from aiogram import Bot
from core.database import AsyncSessionLocal
from core.models import Lead
from sqlalchemy import select, update
import asyncio
from datetime import datetime, timedelta

# ТОКЕН ОСНОВНОГО БОТА
BOT_TOKEN = "8299974277:AAFAWM4bmztjJRQmLdEn62-Iy57HnCm83-M"
bot = Bot(token=BOT_TOKEN)

# ШАБЛОНЫ СООБЩЕНИЙ
SCENARIOS = {
    "first_contact": "Привет, {first_name}! Заметили, ты интересуешься TON и майнингом. У нас 25% в месяц + бонусный майнинг. Хочешь посчитать доход? Напиши /calculator в @cruptos023bot",
    "follow_up_1h": "Ты уже считал доход? 200 TON → 50 TON/мес + бонусный майнинг! Жду тебя: @cruptos023bot",
    "follow_up_24h": "Вот как другие зарабатывают: [скрин выплат]\nТвой шанс — прямо сейчас: @cruptos023bot",
    "follow_up_3d": "Специально для тебя: бонус +10% на первый депозит! Минималка — 10 TON. Пиши в @cruptos023bot",
}

async def send_message(user_id: int, text: str) -> bool:
    try:
        await bot.send_message(user_id, text, disable_web_page_preview=True)
        print(f"[РАССЫЛКА] Отправлено → {user_id}: {text[:50]}...")
        return True
    except Exception as e:
        print(f"[ОШИБКА] Не удалось отправить {user_id}: {e}")
        return False

async def outreach_cycle():
    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()

        # === 1. ПЕРВОЕ КОНТАКТНОЕ СООБЩЕНИЕ ===
        new_leads_result = await db.execute(
            select(Lead).where(Lead.status == 'not_contacted')
        )
        for lead in new_leads_result.scalars():
            first_name = lead.first_name or lead.username or "друг"
            text = SCENARIOS["first_contact"].format(first_name=first_name)
            if await send_message(lead.user_id, text):
                lead.status = 'contacted'
                lead.last_contact = now
                lead.contact_attempts = 1

        # === 2. FOLLOW-UP: 1 ЧАС ===
        hour_ago = now - timedelta(hours=1)
        leads_1h_result = await db.execute(
            select(Lead).where(
                Lead.status == 'contacted',
                Lead.last_contact <= hour_ago,
                Lead.contact_attempts == 1
            )
        )
        for lead in leads_1h_result.scalars():
            if await send_message(lead.user_id, SCENARIOS["follow_up_1h"]):
                lead.contact_attempts = 2
                lead.last_contact = now

        # === 3. FOLLOW-UP: 24 ЧАСА ===
        day_ago = now - timedelta(hours=24)
        leads_24h_result = await db.execute(
            select(Lead).where(
                Lead.status == 'contacted',
                Lead.last_contact <= day_ago,
                Lead.contact_attempts == 2
            )
        )
        for lead in leads_24h_result.scalars():
            if await send_message(lead.user_id, SCENARIOS["follow_up_24h"]):
                lead.contact_attempts = 3
                lead.last_contact = now

        # === 4. FOLLOW-UP: 3 ДНЯ ===
        three_days_ago = now - timedelta(days=3)
        leads_3d_result = await db.execute(
            select(Lead).where(
                Lead.status == 'contacted',
                Lead.last_contact <= three_days_ago,
                Lead.contact_attempts == 3
            )
        )
        for lead in leads_3d_result.scalars():
            if await send_message(lead.user_id, SCENARIOS["follow_up_3d"]):
                lead.status = 'followed_up'
                lead.contact_attempts = 4
                lead.last_contact = now

        await db.commit()
        print(f"[РАССЫЛКА] Цикл завершён: {now.strftime('%H:%M:%S')}")

# === ЗАПУСК КАЖДЫЕ 30 МИНУТ ===
async def start_outreach():
    print("[РАССЫЛКА] Автоматическая рассылка запущена...")
    while True:
        try:
            await outreach_cycle()
        except Exception as e:
            print(f"[КРИТИЧЕСКАЯ ОШИБКА] outreach_cycle: {e}")
        await asyncio.sleep(1800)  # 30 минут