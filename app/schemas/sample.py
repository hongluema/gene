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
    gender: Literal["male", "female"] | None = None
    age: conint(gt=0, le=150) | None = None
    program_id: StrictStr
    org_id: StrictStr
    sample_data_id: StrictStr | None = None
    sample_data_name: StrictStr | None = None
    order_id: StrictStr | None = None
    desc: StrictStr | None = None
    # 新增字段，设为可选
    receive_time: datetime | None = None
    report_date: datetime | None = None
    test_user: StrictStr | None = None
    see_user: StrictStr | None = None
    usable: int | None = None


class SampleCreate(SampleBase):
    pass


class SampleUpdate(BaseModel):
    sample_id: StrictStr
    code: StrictStr | None = None
    name: StrictStr | None = None
    type: Literal["fullBlood"] | None = None
    process: Literal["progressing", "progressed"] | None = None
    user_id: StrictStr | None = None
    phone: StrictStr | None = None
    id_number: StrictStr | None = None
    gender: Literal["male", "female"] | None = None
    age: conint(gt=0, le=150) | None = None
    program_id: StrictStr | None = None
    org_id: StrictStr | None = None
    sample_data_id: StrictStr | None = None
    sample_data_name: StrictStr | None = None
    order_id: StrictStr | None = None
    desc: StrictStr | None = None
    # 新增字段
    receive_time: datetime | None = None
    report_date: datetime | None = None
    test_user: StrictStr | None = None
    see_user: StrictStr | None = None
    usable: int | None = None


class SampleRead(SampleBase):
    sample_id: StrictStr
    created_at: datetime
    updated_at: datetime
    program_name: str | None = None

    class Config:
        from_attributes = True