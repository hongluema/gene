from pydantic import BaseModel


class WxLoginRequest(BaseModel):
    code: str


class WxLoginResponse(BaseModel):
    openid: str
    session_key: str
    unionid: str | None = None

