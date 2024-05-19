from app.db.database import async_session
from app.db.models import Sitting


async def add_sitting(new_sitting: Sitting) -> None:
    async with async_session() as session:
        session.add(new_sitting)
        session.commit()
