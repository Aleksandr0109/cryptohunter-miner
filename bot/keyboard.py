# bot/keyboard.py — v3.0: ТОЛЬКО КНОПКА MINI APP
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

def main_menu():
    """
    Главное меню — одна кнопка: Открыть майнер
    """
    btn_webapp = KeyboardButton(
        text="Открыть майнер",
        web_app=WebAppInfo(url="https://pliable-unpunctuating-stacey.ngrok-free.dev")  # ← ПОЗЖЕ ЗАМЕНИ
    )
    kb = ReplyKeyboardMarkup(
        keyboard=[[btn_webapp]],
        resize_keyboard=True
    )
    return kb