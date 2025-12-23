from pydantic import BaseModel
from pydantic.types import StrictStr


class VerifySmsCodeRequest(BaseModel):
    phone: StrictStr
    code: StrictStr


class SendSmsCodeRequest(BaseModel):
    phone: StrictStr