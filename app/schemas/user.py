from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    mobile: str
    avatar: str | None = None
    nickname: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # 允许直接从 ORM 模型实例转换
