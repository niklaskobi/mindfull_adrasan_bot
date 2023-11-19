# schemas.py
from pydantic import BaseModel
from typing import Optional


class SittingCreate(BaseModel):
    chat_id: str
    user_id: str
    minutes: int
