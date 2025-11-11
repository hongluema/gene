from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    mobile: str
    avatar: str | None = ""
    nickname: str | None = ""


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    mobile: str | None = None
    avatar: str | None = None
    nickname: str | None = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
