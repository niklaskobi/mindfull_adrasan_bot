from datetime import datetime, timedelta, date

from sqlalchemy import delete
from sqlalchemy import func, distinct, cast, Date, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas


async def get_sitting(session: AsyncSession, sitting_id: int):
    result = await session.execute(select(models.Sitting).filter(models.Sitting.id == sitting_id))
    return result.scalars().first()


async def create_sitting(session: AsyncSession, sitting: schemas.SittingCreate):
    db_sitting = models.Sitting(
        chat_id=sitting.chat_id,
        user_id=sitting.user_id,
        duration_m=sitting.duration_m
    )
    session.add(db_sitting)
    await session.commit()
    await session.refresh(db_sitting)
    return db_sitting


async def remove_sittings_at_date(session: AsyncSession, user_id: int, chat_id: int, date: date):
    result = await session.execute(
        delete(models.Sitting)
        .where(func.date(models.Sitting.created_at) == date)
        .where(models.Sitting.user_id == str(user_id))
        .where(models.Sitting.chat_id == str(chat_id))
    )
    await session.commit()
    return result.rowcount


async def get_minutes_current_day(session: AsyncSession, chat_id: int):
    """
    Calculate the sum of all meditation minutes for the current day for the current chat_id
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    query = select(
        func.sum(models.Sitting.duration_m)
    ).filter(
        models.Sitting.chat_id == str(chat_id),
        models.Sitting.created_at >= today,
        models.Sitting.created_at < tomorrow
    )

    result = await session.execute(query)

    return result.scalar()


async def get_user_stats(session: AsyncSession, user_id: int):
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    # Define the main query with all necessary calculations
    stats_query = select(
        func.sum(models.Sitting.duration_m).label('total_duration'),
        func.avg(models.Sitting.duration_m).label('average_duration'),
        func.count().label('total_entries'),
        func.min(models.Sitting.created_at).label('first_entry_date'),
        func.max(models.Sitting.created_at).label('last_entry_date'),
        func.count(distinct(cast(models.Sitting.created_at, Date))).label('days_with_entries'),
        func.count(distinct(case(
            (cast(models.Sitting.created_at, Date) >= start_of_month, cast(models.Sitting.created_at, Date)),
        ))).label('current_month_days')
    ).where(models.Sitting.user_id == str(user_id))

    # Execute the query
    stats_result = await session.execute(stats_query)
    return stats_result.first()


async def get_week_stats_from_db(session: AsyncSession, chat_id: int):
    today = datetime.now().date()
    today_end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago = today - timedelta(days=7)
    query = select(
        func.sum(models.Sitting.duration_m),
        func.date(models.Sitting.created_at)
    ).filter(models.Sitting.chat_id == str(chat_id),
             models.Sitting.created_at >= seven_days_ago,
             models.Sitting.created_at <= today_end_of_day). \
        group_by(func.date(models.Sitting.created_at)). \
        order_by(func.date(models.Sitting.created_at))

    result = await session.execute(query)
    return result.all()