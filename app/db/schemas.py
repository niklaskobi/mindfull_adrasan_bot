# schemas.py
from pydantic import BaseModel
from typing import Optional


class SittingCreate(BaseModel):
    user_id: str
    minutes: int
