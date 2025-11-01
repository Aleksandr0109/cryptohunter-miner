import asyncio
import logging
from sqlalchemy import select, func
from core.database import AsyncSessionLocal
from core.models import Lead

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_leads():
    async with AsyncSessionLocal() as db:
        # Общее количество лидов
        result = await db.execute(select(func.count(Lead.id)))
        total_leads = result.scalar()
        logger.info(f"📊 Всего лидов в базе: {total_leads}")

        if total_leads > 0:
            # Лиды по источникам (если есть source_type)
            try:
                result = await db.execute(
                    select(Lead.source_type, func.count(Lead.id))
                    .group_by(Lead.source_type)
                )
                logger.info("📈 Лиды по источникам:")
                for source_type, count in result:
                    logger.info(f"   {source_type}: {count}")
            except Exception as e:
                logger.info("ℹ️ Поле source_type еще не добавлено")

            # Лиды по статусу
            result = await db.execute(
                select(Lead.conversion_status, func.count(Lead.id))
                .group_by(Lead.conversion_status)
            )
            logger.info("🎯 Лиды по статусу:")
            for status, count in result:
                logger.info(f"   {status}: {count}")

            # Топ лидов по баллам
            result = await db.execute(
                select(Lead)
                .order_by(Lead.interest_score.desc())
                .limit(5)
            )
            logger.info("🏆 Топ-5 лидов по баллам:")
            for lead in result.scalars():
                logger.info(f"   👤 {lead.user_id} | 📊 {lead.interest_score} | 📍 {lead.source_channel}")

            # Последние лиды (используем found_at вместо found_date)
            result = await db.execute(
                select(Lead)
                .order_by(Lead.found_at.desc())  # ИЗМЕНИЛ НА found_at
                .limit(5)
            )
            logger.info("🕒 Последние 5 лидов:")
            for lead in result.scalars():
                logger.info(f"   👤 {lead.user_id} | 📅 {lead.found_at} | 📍 {lead.source_channel}")

        else:
            logger.info("❌ В базе нет лидов")

if __name__ == "__main__":
    asyncio.run(show_leads())