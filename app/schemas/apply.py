from datetime import datetime
from typing import Literal
from pydantic import BaseModel, conint
from pydantic.types import StrictStr


class ApplyBase(BaseModel):
    apply_user_id: StrictStr
    apply_user_phone: StrictStr | None = None
    sample_id: StrictStr
    type: conint(ge=1, le=2)  # 1是作废，2是修改
    reason: StrictStr | None = None


class ApplyCreate(ApplyBase):
    pass


class ApplyUpdate(BaseModel):
    apply_id: StrictStr
    apply_user_phone: StrictStr | None = None
    reason: StrictStr | None = None
    status: Literal["pending", "approved", "rejected"] | None = None
    review_time: datetime | None = None


class ApplyReview(BaseModel):
    """审批申请"""
    apply_id: StrictStr
    status: Literal["approved", "rejected"]  # approved-通过, rejected-拒绝
    reviewer_id: StrictStr
    review_comment: StrictStr | None = None


class ApplyRead(ApplyBase):
    apply_id: StrictStr
    status: Literal["pending", "approved", "rejected"]
    reviewer_id: StrictStr | None = None
    review_time: datetime | None = None
    review_comment: StrictStr | None = None
    created_at: datetime
    updated_at: datetime
    usable: int | None = None

    class Config:
        from_attributes = True
