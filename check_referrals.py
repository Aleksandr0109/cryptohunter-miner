# check_referrals.py — ПРОВЕРКА РЕФЕРАЛЬНОЙ СИСТЕМЫ
import asyncio
from core.database import AsyncSessionLocal
from sqlalchemy import text
from rich.console import Console
from rich.table import Table

console = Console()

async def check_referrals():
    async with AsyncSessionLocal() as db:
        try:
            # === 1. Все рефералы ===
            console.print("\n[bold blue]1. Все рефералы (referrals)[/bold blue]")
            result = await db.execute(text("SELECT * FROM referrals ORDER BY created_at DESC"))
            referrals = result.fetchall()

            if not referrals:
                console.print("   Нет рефералов.")
            else:
                table = Table(title="Таблица referrals")
                table.add_column("ID")
                table.add_column("Пригласил")
                table.add_column("Приглашён")
                table.add_column("Уровень")
                table.add_column("Бонус")
                table.add_column("Дата")
                table.add_column("Статус")

                for r in referrals:
                    table.add_row(
                        str(r[0]), str(r[1]), str(r[2]), str(r[3]),
                        str(r[4]), str(r[5]), str(r[6])
                    )
                console.print(table)

            # === 2. Сколько у кого рефералов ===
            console.print("\n[bold green]2. Счётчик рефералов (users)[/bold green]")
            result = await db.execute(
                text("SELECT user_id, username, referral_count FROM users WHERE referral_count > 0 ORDER BY referral_count DESC")
            )
            users = result.fetchall()

            if not users:
                console.print("   Никто не пригласил рефералов.")
            else:
                table = Table(title="Кто сколько пригласил")
                table.add_column("User ID")
                table.add_column("Имя")
                table.add_column("Рефералов")

                for u in users:
                    table.add_row(str(u[0]), u[1] or "—", str(u[2]))
                console.print(table)

            # === 3. Цепочка рефералов ===
            console.print("\n[bold yellow]3. Реферальная цепочка[/bold yellow]")
            result = await db.execute(text("""
                SELECT 
                    r.referrer_id, u1.username AS inviter,
                    r.referred_id, u2.username AS invited,
                    r.level
                FROM referrals r
                JOIN users u1 ON r.referrer_id = u1.user_id
                JOIN users u2 ON r.referred_id = u2.user_id
                ORDER BY r.level, r.created_at
            """))
            chain = result.fetchall()

            if not chain:
                console.print("   Цепочка пуста.")
            else:
                table = Table(title="Цепочка: Кто → Кого")
                table.add_column("Пригласил (ID)")
                table.add_column("Имя")
                table.add_column("→ Приглашён (ID)")
                table.add_column("Имя")
                table.add_column("Уровень")

                for c in chain:
                    table.add_row(
                        str(c[0]), c[1] or "—",
                        str(c[2]), c[3] or "—",
                        str(c[4])
                    )
                console.print(table)

            console.print("\n[bold magenta]РЕФЕРАЛЬНАЯ СИСТЕМА: ДАННЫЕ ВЫГРУЖЕНЫ[/bold magenta]")

        except Exception as e:
            console.print(f"[red]Ошибка: {e}[/red]")

if __name__ == "__main__":
    asyncio.run(check_referrals())