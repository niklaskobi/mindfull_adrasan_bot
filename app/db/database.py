from app.core.consts import DATABASE_URL

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Modify the DATABASE_URL to use asyncpg
db_url_modified = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)

engine = create_async_engine(db_url_modified, echo=False)
async_session = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

Base = declarative_base()
