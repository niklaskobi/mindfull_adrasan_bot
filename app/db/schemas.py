from pydantic import BaseModel
from datetime import datetime


class SittingBase(BaseModel):
    chat_id: str
    user_id: str
    duration_m: int


class SittingCreate(SittingBase):
    pass


class SittingRead(SittingBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
