from datetime import datetime
from pydantic import BaseModel
from pydantic.types import StrictStr


class ProjectBase(BaseModel):
    name: StrictStr
    desc: StrictStr | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: StrictStr | None = None
    desc: StrictStr | None = None


class ProjectRead(ProjectBase):
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

