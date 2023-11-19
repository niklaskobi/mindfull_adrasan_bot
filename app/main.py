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


async def create_sitting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        user_id = update.effective_chat.id
        text = update.message.text.strip()

        # Use regular expression to extract the number of minutes
        match = re.search(r"[+-]?\s*(\d+)", text)
        if not match:
            await context.bot.send_message(chat_id=user_id,
                                           text="Invalid format. Please enter the minutes as '+10', '+ 10', etc.")
            return
        minutes = int(match.group(1))

        logger.warning(f"creating sitting for user {user_id}, message: {text}, minutes: {minutes}")

        # Create and add new meditation record
        new_meditation = Sitting(user_id=str(user_id), duration_m=minutes)
        session.add(new_meditation)
        session.commit()

        # Calculate the sum of all meditation minutes for the current day
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        total_minutes_today = session.query(func.sum(Sitting.duration_m)).\
            filter(Sitting.user_id == str(user_id),
                   Sitting.created_at >= today,
                   Sitting.created_at < tomorrow).scalar()

        logger.warning(f"sitting successfully created. user_id: {user_id}, minutes: {minutes}")
        await context.bot.send_message(chat_id=user_id, text=f"Total meditation minutes today: {total_minutes_today}")


async def update_meta_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Update meta: {text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сорян, не понял команду.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    sittings_handler = MessageHandler(filters.Regex("^\s*\+\s*\d{1,3}$"), create_sitting)
    # counter_meta_handler = MessageHandler(filters.Regex("^\s*\+\s*(мета|meta)\s*$"), update_meta_counter)
    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(sittings_handler)
    application.add_handler(unknown_handler)  # Note: This handler must be added last

    application.run_polling()
