from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from app.db import crud
from app.db.database import async_session
from app.dependencies import logger


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    if chat_id != user_id:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Извините, я не показываю личную статистику в групповом чате.")
        return

    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    async with async_session() as session:
        stats = await crud.get_user_stats(session, user_id)

        # Calculate the percentage of active days
    total_days = (stats.last_entry_date - stats.first_entry_date).days + 1
    active_days_percentage = (stats.days_with_entries / total_days) * 100

    # Calculate the percentage of meditation days in the current month
    total_days_passed_in_current_month = (now - start_of_month).days + 1
    current_month_percentage = (stats.current_month_days / total_days_passed_in_current_month) * 100

    if stats:
        label_width = 20
        text = (
            f"{'Всего минут:'.ljust(label_width)} {int(stats.total_duration / 60)}ч {stats.total_duration % 60}м\n"
            f"{'Всего медитаций:'.ljust(label_width)} {stats.total_entries}\n"
            f"{'Средняя длина:'.ljust(label_width)} {stats.average_duration:.2f}м\n"
            f"{'% за все время:'.ljust(label_width)} {active_days_percentage:.2f}%\n"
            f"{'% за этот месяц:'.ljust(label_width)} {current_month_percentage:.2f}%\n"
        )
        text = f"```\n{text}\n```"

        await context.bot.send_message(
            # chat_id=update.effective_chat.id, text=text, parse_mode='HTML')
            chat_id=update.effective_chat.id, text=text, parse_mode='MarkdownV2')

    else:
        logger.error("No data found for user ID:", user_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Извините, но я не могу найти данные для вашего ID")


