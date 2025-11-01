# bot/dashboard.py
from core.calculator import ProfitCalculator
from decimal import Decimal

def generate_dashboard(user):
    invested = Decimal(user.invested_amount or 0)
    daily_inv = ProfitCalculator.investment_daily(invested)
    daily_free = ProfitCalculator.free_mining_daily(invested)
    total_daily = daily_inv + daily_free
    speed = ProfitCalculator.mining_speed(invested)
    
    # ИСПРАВЛЕНО: правильное вычисление дней за 1 TON
    if daily_free > 0:
        days_per_ton = Decimal('1') / daily_free
    else:
        days_per_ton = Decimal('90')  # базовое значение при нулевом майнинге

    return (
        f"CRYPTOHUNTER MINER - ВАШ ДАШБОРД\n\n"
        f"ИНВЕСТИЦИИ: `{invested:.2f}` TON\n"
        f"├─ Ежедневно: `{daily_inv:.3f}` TON\n"
        f"├─ Еженедельно: `{daily_inv*7:.3f}` TON\n"
        f"└─ Ежемесячно: `{daily_inv*30:.2f}` TON\n\n"
        f"БЕСПЛАТНЫЙ МАЙНИНГ\n"
        f"├─ Скорость: `{speed*100:.0f}%` (+{speed-1:.2%})\n"
        f"├─ Ежедневно: `{daily_free:.4f}` TON\n"
        f"├─ 1 TON за: `{days_per_ton:.1f}` дней\n"
        f"└─ Накоплено: `{user.free_mining_balance:.2f}` TON\n\n"
        f"СЕЙЧАС НАЧИСЛЯЕТСЯ:\n"
        f" `{total_daily:.4f}` TON/день | `{total_daily/24:.4f}` TON/час\n\n"
        f"ДОСТУПНО К ВЫВОДУ: `{user.free_mining_balance:.2f}` TON\n"
        f"ДО МИНИМАЛЬНОГО ВЫВОДА: {'ГОТОВО' if user.free_mining_balance >= 5 else 'Ещё чуть-чуть'}"
    )