# outreach_sender.py — БЕЗОПАСНЫЙ РЕЖИМ (1 аккаунт)
import asyncio
import logging
import random
from datetime import datetime

from telethon import TelegramClient
from telethon.errors import FloodWaitError
from sqlalchemy import select, update

from core.database import AsyncSessionLocal
from core.models import Lead
from dotenv import load_dotenv
import os

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")  # ← ТОТ ЖЕ, ЧТО В lead_scanner.py

client = TelegramClient("scanner_session", API_ID, API_HASH)  # ← ТО ЖЕ СЕССИЯ!
logger = logging.getLogger("outreach")
logging.basicConfig(level=logging.INFO)

# === ШАБЛОНЫ ===
TEMPLATES = [
    "Привет! Вижу, ты интересуешься TON. У нас майнинг с доходом до 15% в месяц. Хочешь узнать?",
    "TON растёт! А ты уже зарабатываешь на майнинге? У нас 0% комиссии. Напиши — расскажу.",
    "Инвестируешь в крипту? У нас пул с доходом 12-18% годовых. Без риска. Хочешь детали?",
    "Майнинг TON — это просто! 0.5 TON в день с 10 TON вложений. Хочешь попробовать?",
]

# === БЕЗОПАСНАЯ РАССЫЛКА ===
async def safe_send():
    await client.start(phone=PHONE)
    logger.info("Безопасная рассылка лидам — запущена")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lead).where(Lead.conversion_status == "found").limit(20)  # ← МАКС 20!
        )
        leads = result.scalars().all()

        if not leads:
            logger.info("Нет лидов для рассылки")
            await client.disconnect()
            return

        sent = 0
        for lead in leads:
            try:
                message = random.choice(TEMPLATES)
                await client.send_message(lead.user_id, message)
                logger.info(f"Отправлено → {lead.user_id}")

                # Обновляем статус
                lead.conversion_status = "contacted"
                lead.contact_attempts += 1
                lead.last_contact = datetime.utcnow()
                sent += 1
                await db.commit()

                # БЕЗОПАСНЫЙ ИНТЕРВАЛ
                await asyncio.sleep(random.uniform(35, 45))  # 35-45 сек между сообщениями

            except FloodWaitError as e:
                logger.warning(f"Флуд: ждём {e.seconds} сек")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                lead.conversion_status = "failed"
                await db.commit()

        logger.info(f"РАССЫЛКА ЗАВЕРШЕНА: {sent} сообщений")

    await client.disconnect()

# === ЦИКЛ: 1 РАЗ В 3 ЧАСА ===
async def main():
    while True:
        try:
            await safe_send()
            logger.info("Ждём 3 часа до следующей рассылки...")
            await asyncio.sleep(3 * 3600)  # 3 часа
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())