from datetime import timedelta, datetime

from sqlalchemy import func, distinct, cast, Date, select, case
from telegram import Update
from telegram.ext import ContextTypes

from app.db.database import async_session
from app.db.models import Sitting
from app.dependencies import logger


async def me_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id != user_id:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Извините, но я могу показать статистику только для вас.")
        return

    data = await get_user_stats(user_id)
    if data:
        label_width = 20
        text = (
            f"{'Всего минут:'.ljust(label_width)} {int(data['total_duration'] / 60)}ч {data['total_duration'] % 60}м\n"
            f"{'Всего медитаций:'.ljust(label_width)} {data['total_entries']}\n"
            f"{'Средняя длина:'.ljust(label_width)} {data['average_duration']:.2f}м\n"
            f"{'% за все время:'.ljust(label_width)} {data['active_days_percentage']:.2f}%\n"
            f"{'% за этот месяц:'.ljust(label_width)} {data['current_month_percentage']:.2f}%\n"
        )
        # text = f"```\n<pre>\n{text}\n</pre>\n```"
        text = f"```\n{text}\n```"

        await context.bot.send_message(
            # chat_id=update.effective_chat.id, text=text, parse_mode='HTML')
            chat_id=update.effective_chat.id, text=text, parse_mode='MarkdownV2')

    else:
        logger.error("No data found for user ID:", user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Извините, но я не могу найти данные для вашего ID")


async def get_user_stats(user_id):
    async with async_session() as session:
        # Get the current date
        now = datetime.now()
        start_of_month = datetime(now.year, now.month, 1)

        # Define the main query with all necessary calculations
        stats_query = select(
            func.sum(Sitting.duration_m).label('total_duration'),
            func.avg(Sitting.duration_m).label('average_duration'),
            func.count().label('total_entries'),
            func.min(Sitting.created_at).label('first_entry_date'),
            func.max(Sitting.created_at).label('last_entry_date'),
            func.count(distinct(cast(Sitting.created_at, Date))).label('days_with_entries'),
            func.count(distinct(case(
                (cast(Sitting.created_at, Date) >= start_of_month, cast(Sitting.created_at, Date)),
            ))).label('current_month_days')
        ).filter(Sitting.user_id == str(user_id))

        # Execute the query
        stats_result = await session.execute(stats_query)
        stats = stats_result.first()

        # Calculate the percentage of active days
        total_days = (stats.last_entry_date - stats.first_entry_date).days + 1
        active_days_percentage = (stats.days_with_entries / total_days) * 100

        # Calculate the percentage of meditation days in the current month
        total_days_passed_in_current_month = (now - start_of_month).days + 1
        current_month_percentage = (stats.current_month_days / total_days_passed_in_current_month) * 100

        return {
            "total_duration": stats.total_duration,
            "average_duration": stats.average_duration,
            "total_entries": stats.total_entries,
            "first_entry_date": stats.first_entry_date,
            "last_entry_date": stats.last_entry_date,
            "active_days_percentage": active_days_percentage,
            "current_month_percentage": current_month_percentage
        }

