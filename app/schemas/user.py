from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

