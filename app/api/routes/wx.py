import httpx
from fastapi import APIRouter, HTTPException, Depends
import requests
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.wx import WxLoginRequest, WxLoginResponse
from app.api.deps import get_db
from app.crud.user import get_user_by_openid, create_user_by_openid


router = APIRouter()


@router.post("/login", response_model=WxLoginResponse)
async def wx_login(payload: WxLoginRequest, db: Session = Depends(get_db)):
    # print(">>>payload", payload)
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise HTTPException(status_code=500, detail="WeChat appid/secret not configured")

    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": payload.code,
        "grant_type": settings.WX_GRANT_TYPE,
    }
    print(">>>params", params)
    # url = f"https://api.weixin.qq.com/sns/jscode2session?appid={params['appid']}&secret={params['secret']}&js_code={params['js_code']}&grant_type=authorization_code"
    # response = requests.get(url)
    # data = response.json()
    # print(">>>data", data)
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

    # 检查用户的 openid 是否在 users 表中存在
    user = get_user_by_openid(db, openid)
    if not user:
        # 如果不存在，创建新用户
        create_user_by_openid(db, openid)

    return WxLoginResponse(openid=openid, session_key=session_key, unionid=data.get("unionid"))
