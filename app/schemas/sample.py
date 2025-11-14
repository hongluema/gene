from datetime import datetime
from typing import Literal
from pydantic import BaseModel
from pydantic.types import StrictStr
from pydantic import conint


class SampleBase(BaseModel):
    code: StrictStr
    name: StrictStr
    type: Literal["fullBlood"]
    process: Literal["progressing", "progressed"]
    user_id: StrictStr
    phone: StrictStr | None = None
    id_number: StrictStr | None = None
    sex: Literal["male", "female"] | None = None
    age: conint(gt=0, le=150) | None = None
    program_id: int
    org_id: int
    sample_data_id: int | None = None
    order_id: int | None = None
    desc: StrictStr | None = None


class SampleCreate(SampleBase):
    pass


class SampleUpdate(BaseModel):
    code: StrictStr | None = None
    name: StrictStr | None = None
    type: Literal["fullBlood"] | None = None
    process: Literal["progressing", "progressed"] | None = None
    user_id: StrictStr | None = None
    phone: StrictStr | None = None
    id_number: StrictStr | None = None
    sex: Literal["male", "female"] | None = None
    age: conint(gt=0, le=150) | None = None
    program_id: int | None = None
    org_id: int | None = None
    sample_data_id: int | None = None
    order_id: int | None = None
    desc: StrictStr | None = None


class SampleRead(SampleBase):
    sample_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
