from datetime import datetime
from typing import Literal
from pydantic import BaseModel, field_validator
from pydantic.types import StrictStr
from pydantic import conint


def _empty_to_none(v: str | None) -> str | None:
    if v is None:
        return None
    v2 = v.strip()
    return v2 if v2 != "" else None


class UserBase(BaseModel):
    name: StrictStr | None = None
    avatar: StrictStr | None = None
    phone: StrictStr | None = None
    id_number: StrictStr | None = None
    gender: StrictStr | None = None
    age: conint(gt=0, le=150) | None = None

    @field_validator("name", "avatar", "phone", "id_number")
    @classmethod
    def empty_strings_as_none(cls, v: str | None):
        return _empty_to_none(v)


class UserCreate(UserBase):
    pass

class UserUpdate(UserBase):
    user_id: str


class UserRead(UserBase):
    user_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True