import logging
import re
from datetime import datetime, timedelta

from sqlalchemy import func, cast, distinct, Date
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
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Привет!")


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


async def create_sitting_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
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
        session.add(new_sitting)
        session.commit()

        total_minutes_today = await minutes_current_day(chat_id, session)

        logger.warning(f"Sitting successfully created. user_id: {user_id}, minutes: {minutes}")
        await context.bot.send_message(chat_id=chat_id, text=f"={total_minutes_today}")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = []
    try:
        current_jobs = context.job_queue.get_jobs_by_name(name)
    except Exception as e:
        logger.warning(f"Error getting jobs: {e}")

    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_daily_job(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    with SessionLocal() as session:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

        # args[0] should contain the time for the timer in seconds
        # check if args[0] is a time string in format HH:MM
        if len(context.args) > 0 and re.match(r"^\d{1,2}:\d{1,2}$", context.args[0]):
            # get time from context.args[0]
            time = context.args[0]
            # create date.time object
            due = datetime.combine(datetime.today().date(), datetime.strptime(time, "%H:%M").time())
            job_removed = remove_job_if_exists(str(chat_id), context)
            context.job_queue.run_daily(week_stats_from_job, due, chat_id=chat_id, name=str(chat_id), data=due)
            text = "Таймер успешно установлен на " + time + " по UTC."
            if job_removed:
                text += " Старый таймер удален."
            await update.effective_message.reply_text(text)

        else:
            await update.effective_message.reply_text(
                "Сорри, не могу распознать. Пожалуйста, введите время в формате 'HH:MM'")
            return


async def create_sitting_on_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
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
        session.add(new_sitting)
        session.commit()

        # if date is today, send the total minutes
        if date == datetime.now().date():
            total_minutes_today = await minutes_current_day(chat_id, session)
            await context.bot.send_message(chat_id=chat_id, text=f"={total_minutes_today}")
        else:
            # format date in form of 01.11.2023
            d = date.strftime("%d.%m.%Y")
            await context.bot.send_message(chat_id=chat_id, text=f"Медитация успешно добавлена на {d}")


async def minutes_current_day(chat_id, session):
    # Calculate the sum of all meditation minutes for the current day for the current chat_id
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    total_minutes_today = session.query(func.sum(Sitting.duration_m)). \
        filter(Sitting.chat_id == str(chat_id),
               Sitting.created_at >= today,
               Sitting.created_at < tomorrow).scalar()
    return total_minutes_today


async def week_stats_from_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_week_stats_to_chat(update.effective_chat.id, context)


async def week_stats_from_job(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await send_week_stats_to_chat(job.chat_id, context)


async def send_week_stats_to_chat(chat_id, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        stats = await get_week_stats_from_db(chat_id, session)
        # Pretty print the stats
        stats = "\n".join([f"{day.strftime('%d.%m.%Y')}: {minutes} мин" for minutes, day in stats])
        await context.bot.send_message(chat_id=chat_id, text=f"Статистика за последнюю неделю:\n{stats}")


async def my_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with SessionLocal() as session:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        if chat_id != user_id:
            await context.bot.send_message(chat_id=chat_id,
                                           text="Извините, но я могу показать статистику только для вас.")
            return

        data = await get_my_stats_from_db(user_id, session)
        if data:
            total_duration, average_duration, total_entries, first_entry_date, last_entry_date = data
            active_days_percentage = await get_percentage_active_days(user_id, session)
            # active_days_percentage = round(active_days_percentage, 2)
            last_streak = await get_streak_stats_from_db(user_id, session)
            label_width = 30
            value_width = 10
            text = (
                f"{'Всего минут:'.ljust(label_width)} {int(total_duration / 60)}ч {total_duration % 60}м\n"
                f"{'Всего медитаций:'.ljust(label_width)} {total_entries}\n"
                f"{'Средняя длина:'.ljust(label_width)} {average_duration:.2f}м\n"
                f"{'% дней с медитациями:'.ljust(label_width)} {active_days_percentage:.2f}%\n"
                f"{'Стрик:'.ljust(label_width)} {last_streak} дней"
            )
            text = f"```\n<pre>\n{text}\n</pre>\n```"
            text = f"```\n{text}\n```"

            await context.bot.send_message(
                # chat_id=update.effective_chat.id, text=text, parse_mode='HTML')
                chat_id=update.effective_chat.id, text=text, parse_mode='MarkdownV2')

        else:
            print("No data found for user ID:", user_id)


async def get_week_stats_from_db(chat_id, session):
    # Get minutes for the previous 7 days
    today = datetime.now().date()
    today_end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago = today - timedelta(days=7)
    previous_days = session.query(func.sum(Sitting.duration_m), func.date(Sitting.created_at)). \
        filter(Sitting.chat_id == str(chat_id),
               Sitting.created_at >= seven_days_ago,
               Sitting.created_at <= today_end_of_day). \
        group_by(func.date(Sitting.created_at)). \
        order_by(func.date(Sitting.created_at)).all()
    return previous_days


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


async def get_my_stats_from_db(user_id, session):
    query_data = session.query(
        func.sum(Sitting.duration_m).label('total_duration'),
        func.avg(Sitting.duration_m).label('average_duration'),
        func.count().label('total_entries'),
        func.min(Sitting.created_at).label('first_entry_date'),
        func.max(Sitting.created_at).label('last_entry_date')
    ).filter(Sitting.user_id == str(user_id)).one()
    return query_data


async def update_meta_counter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Update meta: {text}")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Сорри, не понял команду.")


if __name__ == '__main__':
    logger.warning("Starting bot")

    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers
    start_handler = CommandHandler('start', start)
    daily_stats_handler = CommandHandler('today', daily_stats)
    remove_stats_handler = CommandHandler('remove', remove_todays_entries)
    set_daily_midnight_job_handler = CommandHandler('schedule_job', set_daily_job)
    week_stats_handler = CommandHandler('week', week_stats_from_command)
    my_history_handler = CommandHandler('history', my_history)
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
    application.add_handler(my_history_handler)
    application.add_handler(add_sittings_today_handler)
    application.add_handler(add_sittings_on_date_handler)
    application.add_handler(set_daily_midnight_job_handler)
    application.add_handler(unknown_handler)  # Note: This handler must be added last

    logger.warning("Bot started")

    # application.run_polling()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
