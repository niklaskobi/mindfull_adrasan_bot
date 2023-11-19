import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

from app.core.consts import BOT_TOKEN

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logging.getLogger('httpx').setLevel(logging.WARNING)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Здаров!")


async def update_meditation_minutes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Update meditation: {text}")


async def update_meta_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Update meta: {text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сорян, не понял команду.")


if __name__ == '__main__':
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    counter_minutes_handler = MessageHandler(filters.Regex("^\s*[+-]\s*\d{1,3}$"), update_meditation_minutes)
    counter_meta_handler = MessageHandler(filters.Regex("^\s*\+\s*(мета|meta)\s*$"), update_meta_counter)
    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(counter_minutes_handler)
    application.add_handler(counter_meta_handler)
    application.add_handler(unknown_handler)  # Note: This handler must be added last

    application.run_polling()
