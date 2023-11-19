# models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Sitting(Base):
    __tablename__ = 'sittings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    duration_m = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
