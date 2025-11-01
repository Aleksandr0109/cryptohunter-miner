# core/calculator.py
from decimal import Decimal

class ProfitCalculator:
    monthly_rate = Decimal('0.25')
    base_mining_days = 90

    @staticmethod
    def investment_daily(amount: Decimal) -> Decimal:
        return amount * ProfitCalculator.monthly_rate / 30

    @staticmethod
    def mining_speed(invested: Decimal) -> Decimal:
        acceleration = (invested // 40) * Decimal('0.01')
        return Decimal('1.0') + acceleration

    @staticmethod
    def free_mining_daily(invested: Decimal) -> Decimal:
        base_daily = Decimal('1') / ProfitCalculator.base_mining_days
        speed = ProfitCalculator.mining_speed(invested)
        return base_daily * speed

    @staticmethod
    def total_daily_income(invested: Decimal) -> Decimal:
        return ProfitCalculator.investment_daily(invested) + ProfitCalculator.free_mining_daily(invested)

    # ДОБАВЛЕНО для совместимости с handlers.py
    @staticmethod
    def total_daily(amount: Decimal) -> Decimal:
        """Алиас для total_daily_income для совместимости"""
        return ProfitCalculator.total_daily_income(amount)