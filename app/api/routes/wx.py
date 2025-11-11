import httpx
from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.schemas.wx import WxLoginRequest, WxLoginResponse


router = APIRouter()


@router.post("/login", response_model=WxLoginResponse)
async def wx_login(payload: WxLoginRequest):
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise HTTPException(status_code=500, detail="WeChat appid/secret not configured")

    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": payload.code,
        "grant_type": settings.WX_GRANT_TYPE,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(settings.WX_JSCODE2SESSION_URL, params=params)
        data = resp.json()
        print(">>>data", data)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"WeChat API request failed: {e}")

    # WeChat error handling
    if isinstance(data, dict) and data.get("errcode") not in (None, 0):
        raise HTTPException(status_code=400, detail={"errcode": data.get("errcode"), "errmsg": data.get("errmsg")})

    openid = data.get("openid")
    session_key = data.get("session_key")
    if not openid or not session_key:
        raise HTTPException(status_code=400, detail="WeChat response missing openid/session_key")

    return WxLoginResponse(openid=openid, session_key=session_key, unionid=data.get("unionid"))
