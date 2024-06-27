from datetime import datetime, timedelta, date, timezone

import pytz
from sqlalchemy import delete
from sqlalchemy import func, distinct, cast, Date, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from . import models, schemas
from ..config import TIME_ZONE


async def create_sitting(session: AsyncSession, sitting: schemas.SittingCreate):
    db_sitting = models.Sitting(
        chat_id=sitting.chat_id,
        user_id=sitting.user_id,
        duration_m=sitting.duration_m,
        created_at=sitting.created_at
    )
    session.add(db_sitting)
    await session.commit()
    await session.refresh(db_sitting)
    return db_sitting


async def remove_sittings_at_date(session: AsyncSession, user_id: int, chat_id: int, date: date):
    result = await session.execute(
        delete(models.Sitting)
        .where(func.date(func.timezone(TIME_ZONE, models.Sitting.created_at)) == date)
        .where(models.Sitting.user_id == str(user_id))
        .where(models.Sitting.chat_id == str(chat_id))
    )
    await session.commit()
    return result.rowcount


async def get_minutes_current_day(session: AsyncSession, chat_id: int):
    """
    Calculate the sum of all meditation minutes for the current day for the current chat_id, considering the specified timezone.
    """
    tz = pytz.timezone(TIME_ZONE)
    today = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
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
    now = datetime.now(pytz.timezone(TIME_ZONE))
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
    today_start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end_of_day = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    seven_days_ago = today_start_of_day - timedelta(days=7)
    query = select(
        func.sum(models.Sitting.duration_m),
        func.date(func.timezone(TIME_ZONE, models.Sitting.created_at)).label('adjusted_date')
    ).filter(
        models.Sitting.chat_id == str(chat_id),
        models.Sitting.created_at >= seven_days_ago,
        models.Sitting.created_at <= today_end_of_day
    ).group_by(
        'adjusted_date'
    ).order_by(
        'adjusted_date'
    )

    result = await session.execute(query)
    return result.all()
