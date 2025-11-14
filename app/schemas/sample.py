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
    project_id: StrictStr
    organization_id: StrictStr
    desc: StrictStr | None = None


class SampleCreate(SampleBase):
    pass


class SampleUpdate(BaseModel):
    sample_number: StrictStr | None = None
    name: StrictStr | None = None
    type: Literal["fullBlood"] | None = None
    process: Literal["progressing", "progressed"] | None = None
    user_id: StrictStr | None = None
    project_id: StrictStr | None = None
    organization_id: StrictStr | None = None
    desc: StrictStr | None = None


class SampleRead(SampleBase):
    sample_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

