from pydantic import BaseModel


class WxLoginRequest(BaseModel):
    code: str


class WxLoginResponse(BaseModel):
    openid: str
    session_key: str
    unionid: str | None = None
    user_id: str


class WxDecryptPhoneRequest(BaseModel):
    code: str  # 微信登录 code
    phoneCode: str | dict  # 手机号授权 code (对象或 JSON 字符串，包含 encryptedData 和 iv)


class WxDecryptPhoneResponse(BaseModel):
    phone: str  # 解密后的手机号
