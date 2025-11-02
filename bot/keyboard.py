# bot/keyboard.py — v3.0: ТОЛЬКО КНОПКА MINI APP
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import WEBAPP_URL
def main_menu():
    """
    Главное меню — одна кнопка: Открыть майнер
    """
    btn_webapp = KeyboardButton(
        text="Открыть майнер",
        web_app=WebAppInfo(url=WEBAPP_URL)
    )
    kb = ReplyKeyboardMarkup(
        keyboard=[[btn_webapp]],
        resize_keyboard=True
    )
    return kb