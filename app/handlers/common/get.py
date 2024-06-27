from telegram import Update
from telegram.ext import ContextTypes

from app.db import crud
from app.db.database import async_session


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    async with async_session() as session:
        total_minutes_today = await crud.get_minutes_current_day(session=session, chat_id=update.effective_chat.id)
        total_minutes_today = 0 if total_minutes_today is None else total_minutes_today

    await context.bot.send_message(chat_id=chat_id, text=f"Всего минут сегодня: {total_minutes_today}")


async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    async with async_session() as session:
        data = await crud.get_week_stats_from_db(session=session, chat_id=chat_id)
    if data:
        stats = "\n".join([f"{day.strftime('%d.%m.%Y')}: {minutes} мин" for minutes, day in data])
        await context.bot.send_message(chat_id=chat_id, text=f"Статистика за последнюю неделю:\n{stats}")
    else:
        await context.bot.send_message(chat_id=chat_id, text="За последние 7 дней нет данных.")
