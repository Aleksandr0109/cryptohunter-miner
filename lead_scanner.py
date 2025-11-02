# lead_scanner.py — v2.5 — РАСШИРЕННАЯ ВЕРСИЯ С КОНКРЕТНЫМИ СЛОВАМИ И КАТЕГОРИЯМИ
import os
import asyncio
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.functions.contacts import SearchRequest
from aiogram import Bot
from sqlalchemy import select
from dotenv import load_dotenv
from core.models import Lead
from core.database import AsyncSessionLocal

# === Настройка логов ===
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scanner.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === Загрузка данных из .env ===
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
PHONE = os.getenv("PHONE")

if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("Не найдены ключи API_ID, API_HASH или BOT_TOKEN в .env")

bot = Bot(token=BOT_TOKEN)
client = TelegramClient("scanner_session", API_ID, API_HASH)

# === Константы ===
PREDEFINED_CHANNELS = [
    "toncoin", "ton_russia", "whaleston", "toninvest", "ton_community",
    "cryptoru", "cryptodzen", "bitcoin", "blockchain", "mining",
    "investments", "crypto_news", "binance_russia", "coinspot",
    "tonapp", "tonstarter", "tonspace", "getgems", "tonkeeper",
    "tonwhales", "tonfoundation", "tondev", "tontech",
    "cryptohunter", "cryptosignal", "cryptoworld", "cryptolife"
]

# === РАСШИРЕННЫЕ КЛЮЧЕВЫЕ СЛОВА ===

# Базовые крипто-термины (15 баллов)
CRYPTO_BASIC_KEYWORDS = [
    "КРИПТОВАЛЮТА", "CRYPTO", "CRYPTOCURRENCY", "БИТКОИН", "BITCOIN", "BTC", 
    "АЛЬТКОИН", "ALTCOIN", "АЛЬТКОИНЫ", "ALTS", "БЛОКЧЕЙН", "BLOCKCHAIN",
    "NFT", "НФТ", "СТЕЙКИНГ", "STAKING", "СТЕЙБЛКОИН", "STABLECOIN",
    "ЭФИРИУМ", "ETHEREUM", "ETH", "SOLANA", "SOL", "CARDANO", "ADA",
    "POLKADOT", "DOT", "DOGECOIN", "DOGE", "LITECOIN", "LTC", "RIPPLE", "XRP"
]

# TON экосистема (25 баллов)  
TON_ECOSYSTEM_KEYWORDS = [
    "TONCOIN", "TON", "ТОН", "THEOPENNETWORK", "TON WALLET", "TON КОШЕЛЕК",
    "TONKEEPER", "TON SPACE", "TON DEFI", "TON DNS", "TON APPS", "TON APPLICATIONS",
    "TON FOUNDATION", "TON EXPLORER", "TONSCAN", "TONVIEWER", "GETGEMS",
    "TON BRIDGE", "TON STAKING", "TON STAKING", "TON SWAP", "TON DEX"
]

# Финансы и инвестиции (20 баллов)
FINANCE_KEYWORDS = [
    "ИНВЕСТИЦИИ", "ВЛОЖЕНИЯ", "ДОХОД", "INVEST", "INVESTMENT", "INCOME", "ПРИБЫЛЬ",
    "ТРЕЙДИНГ", "TRADING", "ТРЕЙДЕР", "TRADER", "CEX", "DEX", "БИРЖА", "EXCHANGE",
    "КРИПТОБИРЖА", "BINANCE", "BYBIT", "KUCOIN", "OKX", "GATEIO", "HUOBI",
    "WHITEBIT", "MEXC", "BITGET", "ПОРТФЕЛЬ", "PORTFOLIO", "ДИВИДЕНДЫ", "DIVIDENDS"
]

# Майнинг (30 баллов - самый высокий!)
MINING_KEYWORDS = [
    "МАЙНИНГ", "ФЕРМА", "НАЧИСЛЕНИЯ", "MINING", "EARN", "ЗАРАБОТОК", "ДОБЫЧА",
    "HASH", "ХЭШ", "МАЙНИТЬ", "МАЙНЕР", "MINER", "МАЙНИНГ ФЕРМА", "MINING FARM",
    "ASIC", "АСИК", "VIDEOCARD", "ВИДЕОКАРТА", "GPU", "РИГ", "RIG", "ПУЛ", "POOL",
    "HASHRATE", "ХЭШРЕЙТ", "CLOUD MINING", "ОБЛАЧНЫЙ МАЙНИНГ"
]

# Жалобы и проблемы (25 баллов)
LOSS_KEYWORDS = [
    "ПОТЕРЯЛ", "СЛИЛ", "ОБМАН", "SCAM", "LOST", "ПРОИГРАЛ", "УБЫТОК", "МОШЕННИК",
    "FRAUD", "ОБМАНУЛИ", "УКРАЛИ", "STOLEN", "HACK", "ВЗЛОМ", "ПРОБЛЕМА", "ПРОБЛЕМЫ",
    "ISSUE", "ERROR", "ОШИБКА", "НЕ РАБОТАЕТ", "NOT WORKING", "КИДАНУЛИ", "ОБМАНУЛИ",
    "ВОРЫ", "THIEF", "УКРАЛИ ДЕНЬГИ", "НЕ ВЫВОДЯТ", "ЗАБЛОКИРОВАЛИ", "BLOCKED",
    "ЗАМОРОЗИЛИ", "FROZEN", "ПОДДЕЛЬНЫЙ", "FAKE", "ЛОХОТРОН", "ПИРАМИДА", "PYRAMID"
]

# === Проверка базы ===
async def check_database_structure():
    from core.database import engine
    from core.models import Base
    logger.info("Проверка структуры БД...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("База данных готова.")
    except Exception as e:
        logger.error(f"Ошибка при проверке БД: {e}")

# === Получение каналов из списка ===
async def get_predefined_channels():
    channels_to_scan = []
    logger.info("Получаем каналы из списка для сканирования...")
    
    for channel in PREDEFINED_CHANNELS:
        try:
            entity = await client.get_entity(channel)
            if entity:
                channels_to_scan.append({
                    "id": entity.id,
                    "title": getattr(entity, "title", channel),
                    "username": getattr(entity, "username", ""),
                    "participants_count": getattr(entity, "participants_count", 0),
                    "source": "predefined"
                })
                logger.info(f"Добавлен канал из списка: {channel}")
        except Exception as e:
            logger.warning(f"Не удалось получить {channel}: {e}")
        await asyncio.sleep(0.5)
    
    return channels_to_scan

# === Поиск НОВЫХ каналов в диалогах ===
async def search_new_channels_in_dialogs(predefined_channels):
    found_channels = []
    predefined_usernames = {ch["username"].lower() for ch in predefined_channels if ch["username"]}
    predefined_titles = {ch["title"].lower() for ch in predefined_channels}
    
    try:
        logger.info("Ищем НОВЫЕ каналы среди диалогов...")
        async for dialog in client.iter_dialogs(limit=150):
            if dialog.is_channel:
                title = getattr(dialog.entity, "title", "").lower()
                username = getattr(dialog.entity, "username", "").lower()
                
                is_predefined = (username in predefined_usernames or 
                               title in predefined_titles or
                               any(predefined in title for predefined in [c.lower() for c in PREDEFINED_CHANNELS]))
                
                if not is_predefined:
                    keywords = [
                        'ton', 'crypto', 'крипт', 'майнинг', 'инвест', 'биткоин', 
                        'blockchain', 'btc', 'eth', 'bitcoin', 'ethereum', 'трейд',
                        'trade', 'coin', 'монета', 'финанс', 'finance', 'деньги', 
                        'money', 'доход', 'earn', 'профит', 'profit', 'mining',
                        'nft', 'defi', 'web3', 'трейдер', 'trader', 'бирж',
                        'staking', 'стейкинг', 'wallet', 'кошелек', 'altcoin', 'альткоин'
                    ]
                    title_lower = title.lower()
                    
                    if any(k in title_lower for k in keywords):
                        found_channels.append({
                            "id": dialog.entity.id,
                            "title": dialog.entity.title,
                            "username": getattr(dialog.entity, "username", ""),
                            "participants_count": getattr(dialog.entity, "participants_count", 0),
                            "source": "discovered"
                        })
                        logger.info(f"НАЙДЕН НОВЫЙ КАНАЛ: {dialog.entity.title}")
        logger.info(f"Найдено новых каналов из диалогов: {len(found_channels)}")
    except Exception as e:
        logger.error(f"Ошибка при поиске новых каналов: {e}")
    return found_channels

# === Поиск каналов через глобальный поиск ===
async def search_channels_globally(predefined_channels):
    found_channels = []
    predefined_usernames = {ch["username"].lower() for ch in predefined_channels if ch["username"]}
    
    try:
        logger.info("Ищем каналы через глобальный поиск...")
        
        search_keywords = [
            'TON', 'Toncoin', 'TON Wallet', 'Tonkeeper', 'TON DeFi', 'TON DNS',
            'Биткоин', 'Bitcoin', 'BTC', 'Эфириум', 'Ethereum', 'ETH',
            'Криптовалюта', 'Cryptocurrency', 'Crypto', 'Крипта',
            'Blockchain', 'Блокчейн', 'Web3', 'DeFi', 'NFT', 'Майнинг', 'Mining',
            'Инвестиции', 'Investment', 'Трейдинг', 'Trading', 'Биржа', 'Binance',
            'The Open Network', 'TON Foundation', 'Getgems', 'TON Space',
            'Крипто', 'Криптомир', 'Аирдроп', 'Staking', 'Альткоин', 'CEX', 'DEX',
            'Stablecoin', 'Стейблкоин', 'Altcoin', 'Альткоины'
        ]
        
        for keyword in search_keywords:
            try:
                logger.info(f"Ищем по ключевому слову: '{keyword}'")
                result = await client(SearchRequest(q=keyword, limit=50))
                
                new_channels_count = 0
                for chat in result.chats:
                    if hasattr(chat, 'username') and chat.username:
                        username = chat.username.lower()
                        if username not in predefined_usernames:
                            title_lower = chat.title.lower()
                            crypto_keywords = [
                                'ton', 'crypto', 'майнинг', 'инвест', 'биткоин', 'blockchain',
                                'btc', 'eth', 'nft', 'defi', 'web3', 'трейд', 'trade', 'бирж',
                                'wallet', 'кошелек', 'staking', 'стейкинг', 'mining', 'альткоин',
                                'altcoin', 'bitcoin', 'ethereum', 'финанс', 'finance'
                            ]
                            if any(k in title_lower for k in crypto_keywords):
                                channel_info = {
                                    "id": chat.id,
                                    "title": chat.title,
                                    "username": chat.username,
                                    "participants_count": getattr(chat, "participants_count", 0),
                                    "source": "global_search"
                                }
                                if not any(c["id"] == chat.id for c in found_channels):
                                    found_channels.append(channel_info)
                                    new_channels_count += 1
                                    logger.info(f"Найден через поиск: {chat.title} (@{chat.username})")
                
                if new_channels_count > 0:
                    logger.info(f"По ключу '{keyword}' найдено {new_channels_count} новых каналов")
                await asyncio.sleep(3)
                
            except Exception as e:
                logger.warning(f"Ошибка поиска по ключу '{keyword}': {e}")
                continue
                
        logger.info(f"Глобальный поиск завершен. Всего найдено: {len(found_channels)}")
                
    except Exception as e:
        logger.error(f"Ошибка глобального поиска: {e}")
    
    return found_channels

# === ОБНОВЛЕННАЯ ФУНКЦИЯ ОЦЕНКИ ИНТЕРЕСА ===
async def calculate_interest_score(text: str):
    score = 0
    found_keywords = []  # Здесь будут и КАТЕГОРИИ и КОНКРЕТНЫЕ слова
    upper = text.upper()

    # Словари для категорий
    category_keywords = {
        "крипто": CRYPTO_BASIC_KEYWORDS,
        "TON": TON_ECOSYSTEM_KEYWORDS, 
        "финансы": FINANCE_KEYWORDS,
        "майнинг": MINING_KEYWORDS,
        "жалобы": LOSS_KEYWORDS
    }

    # Проверяем каждую категорию
    for category, keywords_list in category_keywords.items():
        category_found = False
        for keyword in keywords_list:
            if keyword in upper:
                # Добавляем КОНКРЕТНОЕ слово
                found_keywords.append(keyword)
                category_found = True
                
                # Начисляем баллы
                if category == "крипто":
                    score += 15
                elif category == "TON":
                    score += 25
                elif category == "финансы":
                    score += 20
                elif category == "майнинг":
                    score += 30
                elif category == "жалобы":
                    score += 25
        
        # Если нашли слова из категории - добавляем и КАТЕГОРИЮ
        if category_found:
            found_keywords.append(category)

    return score, found_keywords

# === Сканирование канала ===
async def scan_channel(channel_info):
    identifier = channel_info["username"] or channel_info["title"]
    source_type = channel_info.get("source", "unknown")
    
    if source_type == "predefined":
        logger.info(f"Читаем канал из списка: {identifier}")
    else:
        logger.info(f"Сканируем НОВЫЙ канал: {identifier}")

    messages_scanned = 0
    leads_found = 0

    try:
        async for message in client.iter_messages(identifier, limit=50):
            if not message.text or not message.sender_id:
                continue
            messages_scanned += 1
            score, keywords = await calculate_interest_score(message.text)
            if score >= 50:
                leads_found += 1
                logger.info(f"Найден лид {message.sender_id} в {identifier} (score={score})")
                await process_lead(message.sender_id, identifier, score, keywords, source_type)
    except Exception as e:
        logger.warning(f"Ошибка при сканировании {identifier}: {e}")
        return 0

    logger.info(f"{identifier}: {messages_scanned} сообщений, {leads_found} лидов")
    return leads_found

# === Обработка лида ===
async def process_lead(user_id, source_channel, score, keywords, source_type):
    try:
        async with AsyncSessionLocal() as db:
            # Проверяем, есть ли уже такой лид
            result = await db.execute(select(Lead).where(Lead.user_id == user_id))
            existing = result.scalar_one_or_none()
            if existing:
                logger.info(f"Лид {user_id} уже существует в БД")
                return

            # Получаем username и имя пользователя
            try:
                user = await client.get_entity(user_id)
                username = getattr(user, "username", None)
                first_name = getattr(user, "first_name", None)
            except Exception as e:
                logger.warning(f"Не удалось получить данные пользователя {user_id}: {e}")
                username = None
                first_name = None

            # Создаём новый лид с корректным datetime
            lead = Lead(
                user_id=user_id,
                username=username,
                first_name=first_name,
                source_channel=source_channel,
                source_type=source_type,
                found_at=datetime.utcnow(),
                interest_score=score,
                keywords_list=keywords,
                contact_attempts=0,
                conversion_status="found",
                last_contact=None,
                notes=None
            )
            db.add(lead)
            await db.commit()

            logger.info(f"✅ ЛИД СОХРАНЁН: {user_id} | @{username or '—'} | {source_channel} | score: {score} | keywords: {keywords}")

    except Exception as e:
        logger.error(f"❌ Ошибка при сохранении лида {user_id}: {e}")
        try:
            await db.rollback()
        except:
            pass

# === Фильтрация каналов ===
async def filter_channels(channels):
    filtered_channels = []
    
    for channel in channels:
        # Безопасная проверка ID
        channel_id = channel.get("id")
        if channel_id is None:
            logger.debug(f"Пропускаем канал без ID: {channel.get('title', 'Unknown')}")
            continue
            
        # Проверяем что ID - число
        if not isinstance(channel_id, int):
            logger.debug(f"Пропускаем канал с некорректным ID: {channel.get('title', 'Unknown')} (ID: {channel_id})")
            continue
            
        # Исключаем каналы с ID < 0 (группы и супергруппы)
        if channel_id < 0:
            logger.debug(f"Пропускаем канал с отрицательным ID: {channel.get('title', 'Unknown')} (ID: {channel_id})")
            continue
            
        # Безопасная проверка количества участников
        participants_count = channel.get("participants_count")
        if participants_count is not None and participants_count > 100000:
            logger.debug(f"Пропускаем слишком большой канал: {channel.get('title', 'Unknown')} ({participants_count} участников)")
            continue
            
        filtered_channels.append(channel)
    
    logger.info(f"После фильтрации осталось {len(filtered_channels)} каналов")
    return filtered_channels

# === Основной процесс ===
async def run_scanner():
    await client.start(phone=PHONE)
    logger.info("🚀 Сканер лидов v2.5 запущен — поиск и сохранение (без рассылки)")

    # Получаем каналы
    predefined_channels = await get_predefined_channels()
    new_channels_from_dialogs = await search_new_channels_in_dialogs(predefined_channels)
    new_channels_from_search = await search_channels_globally(predefined_channels)
    
    # Объединяем и убираем дубли
    all_channels = predefined_channels + new_channels_from_dialogs + new_channels_from_search
    
    # Убираем дубли по ID (только для каналов с корректными ID)
    unique_channels = {}
    for ch in all_channels:
        if isinstance(ch.get("id"), int):
            unique_channels[ch["id"]] = ch
    
    all_channels = list(unique_channels.values())
    
    # Фильтруем каналы
    all_channels = await filter_channels(all_channels)

    logger.info(f"📊 Всего каналов для сканирования: {len(all_channels)}")
    logger.info(f"   • Из списка: {len(predefined_channels)}")
    logger.info(f"   • Новые из диалогов: {len(new_channels_from_dialogs)}") 
    logger.info(f"   • Новые из поиска: {len(new_channels_from_search)}")

    total_leads = 0
    processed_channels = 0

    for channel in all_channels:
        leads_found = await scan_channel(channel)
        total_leads += leads_found
        processed_channels += 1
        
        # Прогресс
        if processed_channels % 10 == 0:
            logger.info(f"📈 Прогресс: {processed_channels}/{len(all_channels)} каналов обработано")
            
        await asyncio.sleep(2)  # защита от флуда

    logger.info(f"✅ Сканирование завершено: {processed_channels}/{len(all_channels)} каналов обработано")
    logger.info(f"🎯 Найдено и сохранено лидов: {total_leads}")
    await client.disconnect()
    return total_leads

# === Статистика по найденным лидам ===
async def show_leads_statistics():
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Lead))
            leads = result.scalars().all()
            
            logger.info(f"📈 СТАТИСТИКА БАЗЫ ДАННЫХ:")
            logger.info(f"   • Всего лидов в БД: {len(leads)}")
            
            # Статистика по источникам
            source_stats = {}
            status_stats = {}
            score_stats = {"high": 0, "medium": 0, "low": 0}
            
            # Статистика по ключевым словам
            keyword_stats = {}
            
            for lead in leads:
                # Статистика по источникам
                source_stats[lead.source_type] = source_stats.get(lead.source_type, 0) + 1
                
                # Статистика по статусам
                status_stats[lead.conversion_status] = status_stats.get(lead.conversion_status, 0) + 1
                
                # Статистика по баллам
                if lead.interest_score >= 70:
                    score_stats["high"] += 1
                elif lead.interest_score >= 50:
                    score_stats["medium"] += 1
                else:
                    score_stats["low"] += 1
                
                # Статистика по ключевым словам
                if lead.keywords_list:
                    for keyword in lead.keywords_list:
                        keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
            
            logger.info(f"   • По источникам: {source_stats}")
            logger.info(f"   • По статусам: {status_stats}")
            logger.info(f"   • По баллам интереса: {score_stats}")
            logger.info(f"   • Топ ключевых слов: {dict(sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:15])}")
            
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")

# === Главный цикл ===
async def main():
    await check_database_structure()
    logger.info("=== 🎯 CRYPTOHUNTER SCANNER v2.5 (РАСШИРЕННАЯ) ===")

    cycle = 0
    while True:
        try:
            cycle += 1
            logger.info(f"=== 🔄 ЦИКЛ #{cycle} ===")
            
            # Показываем статистику перед началом сканирования
            await show_leads_statistics()
            
            leads_found = await run_scanner()

            if leads_found > 0:
                logger.info(f"🎉 УСПЕХ: Сохранено {leads_found} новых лидов. Ждём 2 часа...")
                await asyncio.sleep(7200)  # 2 часа
            else:
                logger.info("⏳ Лидов не найдено. Повтор через 30 минут...")
                await asyncio.sleep(1800)  # 30 минут
                
        except Exception as e:
            logger.error(f"💥 КРИТИЧЕСКАЯ ОШИБКА в main: {e}")
            await asyncio.sleep(300)  # 5 минут на восстановление

# === Запуск приложения ===
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Сканер остановлен пользователем")
    except Exception as e:
        logger.error(f"💥 Фатальная ошибка: {e}")