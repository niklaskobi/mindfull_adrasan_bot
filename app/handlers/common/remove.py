from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from app.db import crud
from app.db.database import async_session


async def remove_today_entries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with async_session() as session:
        today = date.today()
        amount_of_deleted_sessions = await crud.remove_sittings_at_date(session=session, user_id=update.effective_user.id,
                                                                        chat_id=update.effective_chat.id, date=today)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Удалил все ваши сегодняшние минуты ({amount_of_deleted_sessions} записей)")
