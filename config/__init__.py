# config/__init__.py — v6.0: RAILWAY ONLY
import os
from dotenv import load_dotenv

load_dotenv()  # НЕ НУЖНО НА RAILWAY, НО НЕ ВРЕДИТ

# === БАЗА: ТОЛЬКО ИЗ ПЕРЕМЕННЫХ RAILWAY ===
DATABASE_URL = os.getenv("MYSQLURL")

# === ОСТАЛЬНОЕ ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
TONKEEPER_MNEMONIC = os.getenv("TONKEEPER_MNEMONIC")
TONKEEPER_API_KEY = os.getenv("TONKEEPER_API_KEY")
TONCENTER_BASE_URL = os.getenv("TONCENTER_BASE_URL", "https://toncenter.com/api/v3")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://cryptohunter-miner.up.railway.app")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
