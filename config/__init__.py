# config/__init__.py — v7.0: ПОЛНЫЙ НАБОР ПЕРЕМЕННЫХ
from dotenv import load_dotenv
import os

load_dotenv()

# === TELEGRAM ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# === TON ===
TONKEEPER_MNEMONIC = os.getenv("TONKEEPER_MNEMONIC")
TONKEEPER_API_KEY = os.getenv("TONKEEPER_API_KEY")
TONCENTER_API_KEY = os.getenv("TONCENTER_API_KEY")  # ДОБАВИЛИ!
TONCENTER_BASE_URL = os.getenv("TONCENTER_BASE_URL", "https://toncenter.com/api/v3")

# === ВЕБ ===
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://cryptohunter-miner.up.railway.app")

# === DEBUG ===
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
