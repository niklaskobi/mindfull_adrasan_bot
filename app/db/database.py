from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.consts import DB_URL

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


