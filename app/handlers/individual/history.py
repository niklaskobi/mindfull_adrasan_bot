from datetime import timedelta

from sqlalchemy import func, distinct, cast, Date, select
from telegram import Update
from telegram.ext import ContextTypes

from app.db.database import async_session
from app.db.models import Sitting
from app.dependencies import logger


async def me_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id != user_id:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Извините, но я могу показать статистику только для вас.")
        return

    data = await get_user_stats(user_id)
    if data:
        label_width = 30
        text = (
            f"{'Всего минут:'.ljust(label_width)} {int(data['total_duration'] / 60)}ч {data['total_duration'] % 60}м\n"
            f"{'Всего медитаций:'.ljust(label_width)} {data['total_entries']}\n"
            f"{'Средняя длина:'.ljust(label_width)} {data['average_duration']:.2f}м\n"
            f"{'% дней с медитациями:'.ljust(label_width)} {data['active_days_percentage']:.2f}%\n"
            f"{'Серия:'.ljust(label_width)} {data['last_streak']}\n"
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
        # Query all necessary statistics and date range for percentage calculation
        stats_query = select(
            func.sum(Sitting.duration_m).label('total_duration'),
            func.avg(Sitting.duration_m).label('average_duration'),
            func.count().label('total_entries'),
            func.min(Sitting.created_at).label('first_entry_date'),
            func.max(Sitting.created_at).label('last_entry_date'),
            func.count(distinct(cast(Sitting.created_at, Date))).label('days_with_entries')
        ).filter(Sitting.user_id == str(user_id))

        # Execute the query
        stats_result = await session.execute(stats_query)
        stats = stats_result.first()

        # Calculate the percentage of active days
        total_days = (stats.last_entry_date - stats.first_entry_date).days + 1
        active_days_percentage = (stats.days_with_entries / total_days) * 100

        # Query to get all distinct dates for streak calculation
        entry_dates_query = select(distinct(cast(Sitting.created_at, Date)).label('entry_date')).\
            filter(Sitting.user_id == str(user_id)).\
            order_by(cast(Sitting.created_at, Date))

        entry_dates_result = await session.execute(entry_dates_query)
        # entry_dates = [date.entry_date for date in entry_dates_result.scalars()]
        entry_dates = [date for date in entry_dates_result.scalars()]

        # Calculate the last streak
        current_streak = 0
        previous_date = None

        for date in reversed(entry_dates):
            if previous_date is None or previous_date - timedelta(days=1) == date:
                current_streak += 1
            else:
                break  # Break the loop once a gap is found
            previous_date = date

        last_streak = current_streak

        return {
            "total_duration": stats.total_duration,
            "average_duration": stats.average_duration,
            "total_entries": stats.total_entries,
            "first_entry_date": stats.first_entry_date,
            "last_entry_date": stats.last_entry_date,
            "active_days_percentage": active_days_percentage,
            "last_streak": last_streak
        }

