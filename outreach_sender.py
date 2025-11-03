# outreach_sender.py — v3.5 — ПРИНИМАЕТ КЛИЕНТ
import asyncio
import logging
import random
from datetime import datetime
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.models import Lead
from dotenv import load_dotenv
import os

# === ЗАГРУЗКА .ENV ===
load_dotenv()

# === ЛОГИ ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("outreach")

# === УМНЫЕ ШАБЛОНЫ ===
def get_template_for_lead(lead):
    keywords = [k.upper() for k in (lead.keywords_list or [])]

    if any(w in keywords for w in ["ТРЕЙДИНГ", "TRADING", "ТРЕЙДЕР", "TRADER", "БИРЖА", "BINANCE", "BYBIT", "ИНВЕСТИЦИИ"]):
        return (
            "Вижу, ты активно торгуешь! 💹\n"
            "Устал от рыночной волатильности?\n"
            "Наша TON ферма дает стабильные 25% в месяц\n"
            "без рисков торговли.\n\n"
            "💰 Твой депозит в 1000 TON будет приносить\n"
            "250 TON каждый месяц на автомате!"
        )

    elif any(w in keywords for w in ["ПОТЕРЯЛ", "СЛИЛ", "УБЫТОК", "LOST", "SCAM", "ОБМАН", "МОШЕННИК", "УКРАЛИ"]):
        return (
            "Заметил, ты недавно потерял на торговле... 😔\n"
            "Хочешь вернуть с гарантированными 25% в месяц?\n\n"
            "Наша майнинг-ферма TON:\n"
            "• Никаких рисков рынка\n"
            "• Ежедневные выплаты\n"
            "• Начни с бесплатного майнинга!"
        )

    elif any(w in keywords for w in ["МАЙНИНГ", "MINING", "ФЕРМА", "ASIC", "GPU", "РИГ", "ПУЛ"]):
        return (
            "Привет, майнер! ⛏️\n"
            "Устал от шума и счетов за свет?\n\n"
            "Облачный TON-майнинг:\n"
            "• 25% в месяц\n"
            "• Без оборудования\n"
            "• Вывод в любой момент\n\n"
            "Бесплатный тест 3 дня!"
        )

    elif any(w in keywords for w in ["TON", "ТОН", "TONCOIN", "TONKEEPER", "TON SPACE"]):
        return (
            "Привет! Ты в теме TON 🚀\n"
            "Зарабатывай 25% в месяц на майнинге без вложений!\n\n"
            "• Бесплатный старт\n"
            "• Депозит от 10 TON\n"
            "• Вывод ежедневно\n\n"
            "Готов попробовать?"
        )

    elif any(w in keywords for w in ["NFT", "НФТ", "СТЕЙКИНГ", "STAKING", "DEFI"]):
        return (
            "Привет! NFT и стейкинг — круто 🎨\n"
            "А майнинг TON лучше:\n"
            "• 25% vs 3-8% в год\n"
            "• Вывод в любой момент\n"
            "• Без локапа\n\n"
            "Расскажу подробнее?"
        )

    else:
        templates = [
            "Привет! TON-майнинг даёт 25% в месяц. Хочешь пассивный доход?",
            "TON растёт! Зарабатывай на майнинге без рисков. Интересно?",
            "Ищешь доход в крипте? Наш TON-майнинг — 25% в месяц. Старт?",
        ]
        return random.choice(templates)

# === БЕЗОПАСНАЯ РАССЫЛКА ===
async def safe_send(client):
    """Принимает готовый Telethon клиент"""
    logger.info("📨 Рассылка запущена — v3.5")

    async with AsyncSessionLocal() as db:
        leads = (await db.execute(
            select(Lead)
            .where(Lead.conversion_status == "found")
            .limit(20)
        )).scalars().all()

        if not leads:
            logger.info("ℹ️ Нет новых лидов для рассылки")
            return

        sent = 0
        for lead in leads:
            try:
                msg = get_template_for_lead(lead)
                await client.send_message(lead.user_id, msg)
                logger.info(f"✅ ОТПРАВЛЕНО → {lead.user_id} | @{lead.username or '—'}")

                lead.conversion_status = "contacted"
                lead.contact_attempts += 1
                lead.last_contact = datetime.utcnow()
                await db.commit()

                sent += 1
                await asyncio.sleep(random.uniform(35, 45))

            except FloodWaitError as e:
                logger.warning(f"⏳ Флуд! Ждём {e.seconds} сек...")
                await asyncio.sleep(e.seconds + 10)

            except Exception as e:
                logger.error(f"❌ Ошибка → {lead.user_id}: {e}")
                lead.conversion_status = "failed"
                await db.commit()

        logger.info(f"📊 РАССЫЛКА ЗАВЕРШЕНА: {sent} сообщений")

# === ГЛАВНЫЙ ЦИКЛ (для standalone запуска) ===
async def main():
    logger.info("📨 OUTREACH SENDER v3.5 — STARTED")
    
    from telethon import TelegramClient
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    
    while True:
        try:
            # Создаем клиент для standalone режима
            client = TelegramClient("scanner_session", API_ID, API_HASH)
            await client.start()
            
            await safe_send(client)
            await client.disconnect()
            
            logger.info("⏰ Ждём 3 часа до следующей волны...")
            await asyncio.sleep(3 * 3600)  # 3 часа
        except Exception as e:
            logger.error(f"💥 КРИТИЧНАЯ ОШИБКА: {e}")
            await asyncio.sleep(3600)  # 1 час при ошибке

if __name__ == "__main__":
    asyncio.run(main())
