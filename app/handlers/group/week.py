from datetime import datetime, timedelta

from sqlalchemy import select, func
from telegram import Update
from telegram.ext import ContextTypes

from app.db.database import async_session
from app.db.models import Sitting


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    data = await get_week_stats_from_db(chat_id)
    if data:
        stats = "\n".join([f"{day.strftime('%d.%m.%Y')}: {minutes} мин" for minutes, day in data])
        await context.bot.send_message(chat_id=chat_id, text=f"Статистика за последнюю неделю:\n{stats}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="За последние 7 дней нет данных.")


async def get_week_stats_from_db(chat_id):
    async with async_session() as session:
        today = datetime.now().date()
        today_end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
        seven_days_ago = today - timedelta(days=7)
        query = select(
            func.sum(Sitting.duration_m),
            func.date(Sitting.created_at)
        ).filter(Sitting.chat_id == str(chat_id),
                 Sitting.created_at >= seven_days_ago,
                 Sitting.created_at <= today_end_of_day). \
            group_by(func.date(Sitting.created_at)). \
            order_by(func.date(Sitting.created_at))

        result = await session.execute(query)
        return result.all()
