# config/__init__.py — v3.0: RAILWAY + MYSQLURL + MAINNET
from dotenv import load_dotenv
import os

load_dotenv()

# === TELEGRAM ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === БАЗА ДАННЫХ: ИСПОЛЬЗУЕМ MYSQLURL (Railway) ===
DATABASE_URL = os.getenv("MYSQLURL")

# === TON (MAINNET) ===
TONKEEPER_MNEMONIC = os.getenv("TONKEEPER_MNEMONIC")
TONKEEPER_API_KEY = os.getenv("TONKEEPER_API_KEY")
TONCENTER_BASE_URL = os.getenv("TONCENTER_BASE_URL", "https://toncenter.com/api/v3")

# === ВЕБ-ПРИЛОЖЕНИЕ ===
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://cryptohunter-miner.up.railway.app")

# === ОТЛАДКА ===
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
