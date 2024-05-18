from app.core.consts import DB_URL

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(DB_URL, echo=False)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)