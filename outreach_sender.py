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

# === ОПРЕДЕЛЕНИЕ ЯЗЫКА ПОЛЬЗОВАТЕЛЯ ===
async def detect_language(client, lead):
    """Определяет язык лида: 'ru' или 'en'"""
    try:
        user = await client.get_entity(lead.user_id)
        texts = []
        if user.first_name:
            texts.append(user.first_name)
        if user.last_name:
            texts.append(user.last_name)
        if getattr(user, 'bio', None):
            texts.append(user.bio)

        full_text = " ".join(texts).lower()

        # Если есть кириллица → русский
        if any('а' <= c <= 'я' for c in full_text):
            return 'ru'

        # Если есть англо-крипто-термины → английский
        crypto_en = ['ton', 'crypto', 'mining', 'btc', 'eth', 'defi', 'nft', 'trade', 'binance']
        if any(word in full_text for word in crypto_en):
            return 'en'

        return 'en'  # по умолчанию
    except Exception as e:
        logger.debug(f"Не удалось определить язык для {lead.user_id}: {e}")
        return 'en'

# === МУЛЬТИЯЗЫЧНЫЕ ШАБЛОНЫ ===
TEMPLATES = {
    'ru': {
        'trading': (
            "Вижу, ты активно торгуешь! 💹\n"
            "Устал от рыночной волатильности?\n"
            "Наша TON ферма дает стабильные 25% в месяц\n"
            "без рисков торговли.\n\n"
            "Твой депозит в 1000 TON будет приносить\n"
            "250 TON каждый месяц на автомате!"
        ),
        'loss': (
            "Заметил, ты недавно потерял на торговле... 😔\n"
            "Хочешь вернуть с гарантированными 25% в месяц?\n\n"
            "Наша майнинг-ферма TON:\n"
            "• Никаких рисков рынка\n"
            "• Ежедневные выплаты\n"
            "• Начни с бесплатного майнинга!"
        ),
        'mining': (
            "Привет, майнер! ⛏️\n"
            "Устал от шума и счетов за свет?\n\n"
            "Облачный TON-майнинг:\n"
            "• 25% в месяц\n"
            "• Без оборудования\n"
            "• Вывод в любой момент\n\n"
            "Бесплатный тест 3 дня!"
        ),
        'ton': (
            "Привет! Ты в теме TON 🚀\n"
            "Зарабатывай 25% в месяц на майнинге без вложений!\n\n"
            "• Бесплатный старт\n"
            "• Депозит от 10 TON\n"
            "• Вывод ежедневно\n\n"
            "Готов попробовать?"
        ),
        'nft_defi': (
            "Привет! NFT и стейкинг — круто 🎨\n"
            "А майнинг TON лучше:\n"
            "• 25% vs 3-8% в год\n"
            "• Вывод в любой момент\n"
            "• Без локапа\n\n"
            "Расскажу подробнее?"
        ),
        'default': [
            "Привет! TON-майнинг даёт 25% в месяц. Хочешь пассивный доход?",
            "TON растёт! Зарабатывай на майнинге без рисков. Интересно?",
            "Ищешь доход в крипте? Наш TON-майнинг — 25% в месяц. Старт?",
        ]
    },
    'en': {
        'trading': (
            "I see you're actively trading! 💹\n"
            "Tired of market volatility?\n"
            "Our TON farm gives stable 25% per month\n"
            "without trading risks.\n\n"
            "Your 1000 TON deposit will earn\n"
            "250 TON every month on autopilot!"
        ),
        'loss': (
            "Noticed you recently lost on trading... 😔\n"
            "Want to recover with guaranteed 25% per month?\n\n"
            "Our TON mining farm:\n"
            "• No market risks\n"
            "• Daily payouts\n"
            "• Start with free mining!"
        ),
        'mining': (
            "Hey miner! ⛏️\n"
            "Tired of noise and electricity bills?\n\n"
            "Cloud TON mining:\n"
            "• 25% per month\n"
            "• No hardware\n"
            "• Withdraw anytime\n\n"
            "3-day free trial!"
        ),
        'ton': (
            "Hey! You're into TON 🚀\n"
            "Earn 25% per month on mining with no investment!\n\n"
            "• Free start\n"
            "• Deposit from 10 TON\n"
            "• Daily withdrawals\n\n"
            "Ready to try?"
        ),
        'nft_defi': (
            "Hey! NFT and staking are cool 🎨\n"
            "But TON mining is better:\n"
            "• 25% vs 3-8% per year\n"
            "• Withdraw anytime\n"
            "• No lockup\n\n"
            "Want details?"
        ),
        'default': [
            "Hey! TON mining gives 25% per month. Want passive income?",
            "TON is growing! Earn on mining with no risks. Interested?",
            "Looking for crypto income? Our TON mining — 25% per month. Start?",
        ]
    }
}

def get_template_for_lead(lead, lang='ru'):
    """Возвращает шаблон на нужном языке по ключевым словам"""
    keywords = [k.upper() for k in (lead.keywords_list or [])]
    tmpl = TEMPLATES[lang]

    if any(w in keywords for w in ["ТРЕЙДИНГ", "TRADING", "ТРЕЙДЕР", "TRADER", "БИРЖА", "BINANCE", "BYBIT", "ИНВЕСТИЦИИ", "INVESTMENT"]):
        return tmpl['trading']
    elif any(w in keywords for w in ["ПОТЕРЯЛ", "СЛИЛ", "УБЫТОК", "LOST", "SCAM", "ОБМАН", "МОШЕННИК", "УКРАЛИ"]):
        return tmpl['loss']
    elif any(w in keywords for w in ["МАЙНИНГ", "MINING", "ФЕРМА", "ASIC", "GPU", "РИГ", "ПУЛ"]):
        return tmpl['mining']
    elif any(w in keywords for w in ["TON", "ТОН", "TONCOIN", "TONKEEPER", "TON SPACE"]):
        return tmpl['ton']
    elif any(w in keywords for w in ["NFT", "НФТ", "СТЕЙКИНГ", "STAKING", "DEFI"]):
        return tmpl['nft_defi']
    else:
        return random.choice(tmpl['default'])

# === БЕЗОПАСНАЯ РАССЫЛКА ===
async def safe_send(client):
    """Принимает готовый Telethon клиент"""
    logger.info("Рассылка запущена — v3.5 (мультиязычная)")
    async with AsyncSessionLocal() as db:
        leads = (await db.execute(
            select(Lead)
            .where(Lead.conversion_status == "found")
            .limit(20)
        )).scalars().all()

        if not leads:
            logger.info("Нет новых лидов для рассылки")
            return

        sent = 0
        for lead in leads:
            try:
                # Определяем язык
                lang = await detect_language(client, lead)
                msg = get_template_for_lead(lead, lang)

                await client.send_message(lead.user_id, msg)
                logger.info(f"ОТПРАВЛЕНО [{lang.upper()}] → {lead.user_id} | @{lead.username or '—'}")

                # Обновляем статус в БД
                lead.conversion_status = "contacted"
                lead.contact_attempts += 1
                lead.last_contact = datetime.utcnow()
                await db.commit()
                sent += 1

                # Антифлуд: 35–45 сек
                await asyncio.sleep(random.uniform(35, 45))

            except FloodWaitError as e:
                logger.warning(f"Флуд! Ждём {e.seconds} сек...")
                await asyncio.sleep(e.seconds + 10)
            except Exception as e:
                logger.error(f"Ошибка → {lead.user_id}: {e}")
                lead.conversion_status = "failed"
                await db.commit()

        logger.info(f"РАССЫЛКА ЗАВЕРШЕНА: {sent} сообщений")

# === ГЛАВНЫЙ ЦИКЛ (для standalone запуска) ===
async def main():
    logger.info("OUTREACH SENDER v3.5 — STARTED")
   
    API_ID = int(os.getenv("API_ID"))
    API_HASH = os.getenv("API_HASH")
    PHONE = os.getenv("PHONE")

    if not all([API_ID, API_HASH, PHONE]):
        logger.error("Не хватает API_ID, API_HASH или PHONE в .env")
        return

    while True:
        try:
            # Создаём клиент
            client = TelegramClient("outreach_session", API_ID, API_HASH)
            await client.start(phone=PHONE)
           
            await safe_send(client)
            await client.disconnect()
           
            logger.info("Ждём 3 часа до следующей волны...")
            await asyncio.sleep(3 * 3600)  # 3 часа

        except Exception as e:
            logger.error(f"КРИТИЧНАЯ ОШИБКА: {e}")
            await asyncio.sleep(3600)  # 1 час при ошибке

if __name__ == "__main__":
    asyncio.run(main())
