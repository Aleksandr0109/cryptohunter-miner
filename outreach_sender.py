# outreach_sender.py — БЕЗОПАСНЫЙ РЕЖИМ (1 аккаунт) + УМНЫЕ ШАБЛОНЫ
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
PHONE = os.getenv("PHONE")

client = TelegramClient("scanner_session", API_ID, API_HASH)
logger = logging.getLogger("outreach")
logging.basicConfig(level=logging.INFO)

# === УМНЫЕ ШАБЛОНЫ ПО КЛЮЧЕВЫМ СЛОВАМ ===
def get_template_for_lead(lead):
    """Выбирает шаблон на основе ключевых слов лида"""
    keywords = lead.keywords_list or []
    
    # Приводим к верхнему регистру для проверки
    keywords_upper = [k.upper() for k in keywords]
    
    # === ДЛЯ ТРЕЙДЕРОВ И ИНВЕСТОРОВ ===
    if any(word in keywords_upper for word in ["ТРЕЙДИНГ", "TRADING", "ТРЕЙДЕР", "TRADER", "БИРЖА", "EXCHANGE", "BINANCE", "BYBIT", "INVEST", "ИНВЕСТИЦИИ"]):
        return (
            "Вижу, ты активно торгуешь! 💹\n"
            "Устал от рыночной волатильности?\n\n"
            "Наша TON ферма дает стабильные 25% в месяц\n"
            "без рисков торговли.\n\n"
            "💰 Твой депозит в 1000 TON будет приносить\n"
            "250 TON каждый месяц на автомате!"
        )
    
    # === ДЛЯ ПОТЕРПЕВШИХ УБЫТКИ ===
    elif any(word in keywords_upper for word in ["ПОТЕРЯЛ", "СЛИЛ", "УБЫТОК", "LOST", "SCAM", "ОБМАН", "МОШЕННИК", "УКРАЛИ", "ПРОБЛЕМА", "НЕ ВЫВОДЯТ"]):
        return (
            "Заметил, ты недавно потерял на торговле... 😔\n"
            "Хочешь вернуть с гарантированными 25% в месяц?\n\n"
            "Наша майнинг-ферма TON:\n"
            "• Никаких рисков рынка\n"
            "• Ежедневные выплаты\n"
            "• Начни с бесплатного майнинга!"
        )
    
    # === ДЛЯ МАЙНЕРОВ ===
    elif any(word in keywords_upper for word in ["МАЙНИНГ", "MINING", "ФЕРМА", "ASIC", "VIDEOCARD", "HASHRATE", "ПУЛ", "РИГ", "МАЙНЕР"]):
        return (
            "Привет, майнер! ⛏️\n"
            "Устал от шума и высоких счетов за электричество?\n\n"
            "Переходи на облачный майнинг TON:\n"
            "• 25% в месяц гарантировано\n"
            "• Никакого оборудования\n"
            "• Вывод в любой момент\n\n"
            "Попробуй бесплатный майнинг 3 дня!"
        )
    
    # === ДЛЯ TON ЭКОСИСТЕМЫ ===
    elif any(word in keywords_upper for word in ["TON", "ТОН", "TONCOIN", "TONKEEPER", "TON WALLET", "TON SPACE", "TON DEFI"]):
        return (
            "Привет! Вижу, ты в теме TON 🚀\n"
            "А ты знаешь, что можешь зарабатывать 25% в месяц\n"
            "на майнинге TON без вложений?\n\n"
            "• Начни с бесплатного майнинга\n"
            "• Депозит от 10 TON\n"
            "• Вывод каждый день\n\n"
            "Хочешь попробовать?"
        )
    
    # === ДЛЯ NFT И СТЕЙКИНГА ===
    elif any(word in keywords_upper for word in ["NFT", "НФТ", "СТЕЙКИНГ", "STAKING", "DEFI"]):
        return (
            "Привет! Вижу, ты интересуешься NFT/стейкингом 🎨\n"
            "А пробовал майнинг TON?\n\n"
            "Преимущества перед стейкингом:\n"
            "• 25% vs 3-8% в год\n"
            "• Вывод в любой момент\n"
            "• Никакого lock-up периода\n\n"
            "Давай расскажу подробнее?"
        )
    
    # === ДЛЯ НОВИЧКОВ ===
    elif any(word in keywords_upper for word in ["НОВИЧОК", "НАЧИНАЮ", "ПЕРВЫЙ", "НЕТ ОПЫТА", "КАК НАЧАТЬ"]):
        return (
            "Привет! Вижу, ты только начинаешь в крипто 🚀\n"
            "Хочешь пассивный доход без сложностей?\n\n"
            "Получи 1 TON бесплатно за 3 месяца майнинга\n"
            "и до 25% в месяц на инвестиции!\n\n"
            "Напиши 'Старт' для начала!"
        )
    
    # === УНИВЕРСАЛЬНЫЙ ШАБЛОН ===
    else:
        templates = [
            "Привет! Заметил твой интерес к криптовалютам. У нас майнинг TON с доходом 25% в месяц. Хочешь узнать?",
            "TON показывает отличный рост! А ты уже зарабатываешь на майнинге? У нас 0% комиссии. Рассказать?",
            "Ищешь пассивный доход в крипте? Наш майнинг TON дает до 25% в месяц. Без рисков. Интересует?",
        ]
        return random.choice(templates)

# === БЕЗОПАСНАЯ РАССЫЛКА ===
async def safe_send():
    await client.start(phone=PHONE)
    logger.info("Умная рассылка лидам — запущена")

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Lead).where(Lead.conversion_status == "found").limit(20)
        )
        leads = result.scalars().all()

        if not leads:
            logger.info("Нет лидов для рассылки")
            await client.disconnect()
            return

        sent = 0
        for lead in leads:
            try:
                # Получаем индивидуальный шаблон
                message = get_template_for_lead(lead)
                
                await client.send_message(lead.user_id, message)
                logger.info(f"Отправлено → {lead.user_id} | Ключи: {lead.keywords_list}")

                # Обновляем статус
                lead.conversion_status = "contacted"
                lead.contact_attempts += 1
                lead.last_contact = datetime.utcnow()
                sent += 1
                await db.commit()

                # БЕЗОПАСНЫЙ ИНТЕРВАЛ
                await asyncio.sleep(random.uniform(35, 45))

            except FloodWaitError as e:
                logger.warning(f"Флуд: ждём {e.seconds} сек")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logger.error(f"Ошибка для {lead.user_id}: {e}")
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
            await asyncio.sleep(3 * 3600)
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())