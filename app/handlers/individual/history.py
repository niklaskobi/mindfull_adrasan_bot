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

    data = await get_my_stats_from_db(user_id)
    if data:
        total_duration, average_duration, total_entries, first_entry_date, last_entry_date = data
        # active_days_percentage = await get_percentage_active_days(user_id, session)
        active_days_percentage = 0
        # last_streak = await get_streak_stats_from_db(user_id, session)
        last_streak = 0
        label_width = 30
        text = (
            f"{'Всего минут:'.ljust(label_width)} {int(total_duration / 60)}ч {total_duration % 60}м\n"
            f"{'Всего медитаций:'.ljust(label_width)} {total_entries}\n"
            f"{'Средняя длина:'.ljust(label_width)} {average_duration:.2f}м\n"
            f"{'% дней с медитациями:'.ljust(label_width)} {active_days_percentage:.2f}%\n"
            f"{'Стрик:'.ljust(label_width)} {last_streak} дней"
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


async def get_percentage_active_days(user_id, session):
    # Query to count distinct days with entries and the range of dates
    days_with_entries = session.query(
        func.count(distinct(cast(Sitting.created_at, Date))).label('days_with_entries'),
        func.min(Sitting.created_at).label('first_entry_date'),
        func.max(Sitting.created_at).label('last_entry_date')
    ).filter(Sitting.user_id == str(user_id)).one()

    total_days = (days_with_entries.last_entry_date - days_with_entries.first_entry_date).days + 1
    percentage_of_days_with_entries = (days_with_entries.days_with_entries / total_days) * 100

    return percentage_of_days_with_entries


async def get_streak_stats_from_db(user_id, session):
    # Query to get all distinct dates with entries
    entry_dates = session.query(
        distinct(cast(Sitting.created_at, Date)).label('entry_date')
    ).filter(Sitting.user_id == str(user_id)).order_by(cast(Sitting.created_at, Date)).all()

    # Convert list of tuples to list of dates
    entry_dates = [date.entry_date for date in entry_dates]

    # Calculate the last streak
    last_streak = 0
    current_streak = 0
    previous_date = None

    for date in reversed(entry_dates):
        if previous_date is None or previous_date - timedelta(days=1) == date:
            current_streak += 1
        else:
            break  # Break the loop once a gap is found
        previous_date = date

    last_streak = current_streak

    return last_streak


async def get_my_stats_from_db(user_id):
    async with async_session() as session:
        stmt = select(
            func.sum(Sitting.duration_m).label('total_duration'),
            func.avg(Sitting.duration_m).label('average_duration'),
            func.count().label('total_entries'),
            func.min(Sitting.created_at).label('first_entry_date'),
            func.max(Sitting.created_at).label('last_entry_date')
        ).filter(Sitting.user_id == str(user_id))

        result = await session.execute(stmt)
        return result.first()  # Fetch the first result of the query
