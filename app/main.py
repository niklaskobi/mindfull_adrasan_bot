from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from app.core.consts import BOT_TOKEN
from app.dependencies import logger
from app.handlers.common.add import create_sitting_today, create_sitting_on_date
from app.handlers.common.misc import start, unknown
from app.handlers.common.get import today
from app.handlers.common.remove import remove_today_entries
from app.handlers.group.get import week
from app.handlers.individual.get import stats

if __name__ == '__main__':
    logger.warning("Starting bot")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    daily_stats_handler = CommandHandler('today', today)
    remove_stats_handler = CommandHandler('remove', remove_today_entries)
    week_stats_handler = CommandHandler('week', week)
    me_history_handler = CommandHandler('stats', stats)
    add_sittings_today_handler = MessageHandler(filters.Regex("^\s*\+\s*\d{1,3}$"), create_sitting_today)
    add_sittings_on_date_handler = MessageHandler(filters.Regex("^\s*\+\s*\d{1,3}\s*\d{1,2}\.\d{1,2}\.\d{4}$"),
                                                  create_sitting_on_date)
    # counter_meta_handler = MessageHandler(filters.Regex("^\s*\+\s*(мета|meta)\s*$"), update_meta_counter)
    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(daily_stats_handler)
    application.add_handler(remove_stats_handler)
    application.add_handler(week_stats_handler)
    application.add_handler(me_history_handler)
    application.add_handler(add_sittings_today_handler)
    application.add_handler(add_sittings_on_date_handler)
    application.add_handler(unknown_handler)  # Note: This handler must be added last

    logger.warning("Bot started")

    # application.run_polling()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
