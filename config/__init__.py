# config/__init__.py
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"mysql+aiomysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
# config/__init__.py — ДОБАВЬ В КОНЕЦ
TONKEEPER_MNEMONIC = os.getenv("TONKEEPER_MNEMONIC")
TONKEEPER_API_KEY = os.getenv("TONKEEPER_API_KEY")
TONCENTER_API_KEY = os.getenv("TONCENTER_API_KEY", TONKEEPER_API_KEY)
TONCENTER_BASE_URL = os.getenv("TONCENTER_BASE_URL", "https://testnet.toncenter.com/api/v3")