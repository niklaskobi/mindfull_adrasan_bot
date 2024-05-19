from datetime import datetime, timedelta

from sqlalchemy import func
from telegram import Update
from telegram.ext import ContextTypes

from app.db.database import async_session
from app.db.models import Sitting
from app.dependencies import logger

# TODO LAST STOP make today and add async

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    minutes = await minutes_current_day(chat_id)
    if minutes is None:
        minutes = 0
    await context.bot.send_message(chat_id=chat_id, text=f"Всего минут сегодня: {minutes}")


async def remove_todays_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with async_session() as session:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id

        # Calculate today's date range
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)

        # Query to find today's entries for the current user
        todays_entries = session.query(Sitting). \
            filter(Sitting.user_id == str(user_id),
                   Sitting.chat_id == str(chat_id),
                   Sitting.created_at >= today,
                   Sitting.created_at < tomorrow)

        for entry in todays_entries:
            logger.warning(f"todays_entries: {entry}")
        # Delete the entries
        todays_entries.delete(synchronize_session='fetch')
        session.commit()

        await context.bot.send_message(chat_id=chat_id, text="Удалил все ваши сегодняшние минуты")


async def minutes_current_day(chat_id):
    """
    Calculate the sum of all meditation minutes for the current day for the current chat_id
    """
    async with async_session() as session:
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        total_minutes_today = session.query(func.sum(Sitting.duration_m)). \
            filter(Sitting.chat_id == str(chat_id),
                   Sitting.created_at >= today,
                   Sitting.created_at < tomorrow).scalar()
        return total_minutes_today
