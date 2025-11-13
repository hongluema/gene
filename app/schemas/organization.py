from datetime import datetime
from pydantic import BaseModel
from pydantic.types import StrictStr


class OrganizationBase(BaseModel):
    name: StrictStr
    desc: StrictStr | None = None


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: StrictStr | None = None
    desc: StrictStr | None = None


class OrganizationRead(OrganizationBase):
    organization_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

