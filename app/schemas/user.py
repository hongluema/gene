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
    nickname: StrictStr | None = None
    avatar: StrictStr | None = None
    mobile: StrictStr | None = None
    idCard: StrictStr | None = None
    sex: Literal["male", "female"] | None = None
    age: conint(gt=0, le=150) | None = None

    @field_validator("name", "nickname", "avatar", "mobile", "idCard")
    @classmethod
    def empty_strings_as_none(cls, v: str | None):
        return _empty_to_none(v)


class UserCreate(UserBase):
    openid: StrictStr


class UserUpdate(UserBase):
    pass


class UserRead(UserBase):
    user_id: str
    openid: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
