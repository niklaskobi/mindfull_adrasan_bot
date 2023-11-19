import logging
import re
from datetime import datetime, timedelta

from sqlalchemy import func
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.core.consts import BOT_TOKEN, LOGGER_MAIN
from app.db.database import SessionLocal
from app.db.models import Sitting

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(LOGGER_MAIN)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Здаров!")


async def daily_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        chat_id = update.effective_chat.id
        minutes = await minutes_current_day(chat_id, session)
        if minutes is None:
            minutes = 0
        await context.bot.send_message(chat_id=chat_id, text=f"Всего минут сегодня: {minutes}")


async def remove_todays_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
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


async def create_sitting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        text = update.message.text.strip()

        # Use regular expression to extract the number of minutes
        match = re.search(r"[+-]?\s*(\d+)", text)
        if not match:
            await context.bot.send_message(chat_id=chat_id,
                                           text="Invalid format. Please enter the minutes as '+10', '+ 10', etc.")
            return
        minutes = int(match.group(1))

        logger.warning(f"creating sitting for user: {user_id}, chat: {chat_id}, message: {text}, minutes: {minutes}")

        # Create and add new sitting record
        # todo use pydentics' dataclass to validate the input
        new_sitting = Sitting(chat_id=str(chat_id), user_id=user_id, duration_m=minutes)
        session.add(new_sitting)
        session.commit()

        total_minutes_today = await minutes_current_day(chat_id, session)

        logger.warning(f"sitting successfully created. user_id: {chat_id}, minutes: {minutes}")
        await context.bot.send_message(chat_id=chat_id, text=f"={total_minutes_today}")


async def minutes_current_day(chat_id, session):
    # Calculate the sum of all meditation minutes for the current day for the current chat_id
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    total_minutes_today = session.query(func.sum(Sitting.duration_m)). \
        filter(Sitting.chat_id == str(chat_id),
               Sitting.created_at >= today,
               Sitting.created_at < tomorrow).scalar()
    return total_minutes_today


async def update_meta_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Update meta: {text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сорян, не понял команду.")


if __name__ == '__main__':

    logger.warning("Starting bot")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    daily_stats_handler = CommandHandler('today', daily_stats)
    remove_stats_handler = CommandHandler('remove', remove_todays_entries)
    add_sittings_handler = MessageHandler(filters.Regex("^\s*\+\s*\d{1,3}$"), create_sitting)
    # counter_meta_handler = MessageHandler(filters.Regex("^\s*\+\s*(мета|meta)\s*$"), update_meta_counter)
    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(daily_stats_handler)
    application.add_handler(remove_stats_handler)
    application.add_handler(add_sittings_handler)
    application.add_handler(unknown_handler)  # Note: This handler must be added last

    logger.warning("Bot started")

    application.run_polling()
