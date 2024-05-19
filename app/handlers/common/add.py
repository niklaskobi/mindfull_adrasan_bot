import re
from datetime import datetime, timedelta

from telegram import Update
from telegram.ext import ContextTypes

from app.db.database import async_session
from app.db.handlers import add_sitting
from app.db.models import Sitting
from app.dependencies import logger
from app.handlers.common.today import minutes_current_day


async def create_sitting_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Use regular expression to extract the number of minutes
    match = re.search(r"[+-]?\s*(\d+)", text)
    if not match:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Не могу распознать. Пожалуйста, введите минуты в формате '+10', '+ 10', ...")
        return
    minutes = int(match.group(1))

    logger.warning(
        f"Creating sitting for user: {update.effective_user.username} ({user_id}), chat: {chat_id}, message: {text}, minutes: {minutes}")

    # Create and add new sitting record
    # todo use pydentics' dataclass to validate the input
    new_sitting = Sitting(chat_id=str(chat_id), user_id=user_id, duration_m=minutes)
    await add_sitting(new_sitting)

    total_minutes_today = await minutes_current_day(chat_id)

    logger.warning(f"Sitting successfully created. user_id: {user_id}, minutes: {minutes}")
    await context.bot.send_message(chat_id=chat_id, text=f"={total_minutes_today}")


async def create_sitting_on_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with async_session() as session:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        text = update.message.text.strip()

        # Use regular expression to extract the number of minutes
        match = re.search(r"[+-]?\s*(\d+)\s*(\d{1,2})\.(\d{1,2})\.(\d{4})", text)
        if not match:
            await context.bot.send_message(chat_id=chat_id,
                                           text="Не могу распознать. Пожалуйста, введите минуты в формате '+10 01.11.2023', '+ 10 01.11.2023', ...")
            return

        # Check if the date is valid
        try:
            date = datetime(int(match.group(4)), int(match.group(3)), int(match.group(2)))
            # Check if the date is in the future
            if date > datetime.now():
                await context.bot.send_message(chat_id=chat_id, text="Не могу добавить будущую дату.")
                return
            # Check if date is older than 1 week:
            if date < datetime.now() - timedelta(days=7):
                await context.bot.send_message(chat_id=chat_id,
                                               text="Неверная дата. Дата должна быть не старше 7 дней.")
                return
        except ValueError:
            await context.bot.send_message(chat_id=chat_id,
                                           text="Неверная дата. Пожалуйста, введите дату в формате '+10 01.11.2023', '+ 10 01.11.2023', ...")
            return

        # Insert the sitting into the database
        minutes = int(match.group(1))
        day = int(match.group(2))
        month = int(match.group(3))
        year = int(match.group(4))

        logger.warning(
            f'Creating sitting for user: {update.effective_user.username} ({user_id}), chat: {chat_id}, message: {text}, minutes: {minutes}, date: {day}.{month}.{year}')

        # Create and add new sitting record
        # todo use pydentics' dataclass to validate the input
        new_sitting = Sitting(chat_id=str(chat_id), user_id=user_id, duration_m=minutes,
                              created_at=datetime(year, month, day))
        await add_sitting(new_sitting)

        # if date is today, send the total minutes
        if date == datetime.now().date():
            total_minutes_today = await minutes_current_day(chat_id)
            await context.bot.send_message(chat_id=chat_id, text=f"={total_minutes_today}")
        else:
            # format date in form of 01.11.2023
            d = date.strftime("%d.%m.%Y")
            await context.bot.send_message(chat_id=chat_id, text=f"Медитация успешно добавлена на {d}")
