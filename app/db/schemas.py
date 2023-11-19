# schemas.py
from pydantic import BaseModel
from typing import Optional


class MeditationCreate(BaseModel):
    user_id: str
    minutes: int
