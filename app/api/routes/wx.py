import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from core.config import settings
from schemas.wx import WxDecryptPhoneRequest, WxDecryptPhoneResponse
from common.decorators import log_exceptions

router = APIRouter()


async def _get_access_token() -> str:
    """获取微信 access_token"""
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise HTTPException(status_code=500, detail="微信配置未设置")
    
    url = settings.WX_ACCESS_TOKEN_URL
    params = {
        "grant_type": "client_credential",
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"获取 access_token 失败: {data.get('errmsg', '未知错误')} (errcode: {data.get('errcode')})"
                )
            
            if "access_token" not in data:
                raise HTTPException(status_code=400, detail="未获取到 access_token")
            
            return data["access_token"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"请求微信接口失败: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"连接微信接口失败: {e}")


async def _get_phone_by_code(phone_code: str) -> str:
    """通过 phoneCode 获取手机号（新版本 API）"""
    access_token = await _get_access_token()
    url = settings.WX_GET_PHONE_URL
    params = {"access_token": access_token}
    payload = {"code": phone_code}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, params=params, json=payload, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"获取手机号失败: {data.get('errmsg', '未知错误')} (errcode: {data.get('errcode')})"
                )
            
            phone_info = data.get("phone_info", {})
            phone = phone_info.get("phoneNumber") or phone_info.get("purePhoneNumber")
            
            if not phone:
                raise HTTPException(status_code=400, detail="未获取到手机号")
            
            return phone
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"请求微信接口失败: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"连接微信接口失败: {e}")


async def _get_session_key(code: str) -> dict:
    """通过 code 获取 session_key 和 openid（旧版本 API，用于解密）"""
    if not settings.WX_APPID or not settings.WX_SECRET:
        raise HTTPException(status_code=500, detail="微信配置未设置")
    
    url = settings.WX_JSCODE2SESSION_URL
    params = {
        "appid": settings.WX_APPID,
        "secret": settings.WX_SECRET,
        "js_code": code,
        "grant_type": settings.WX_GRANT_TYPE,
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            if "errcode" in data and data["errcode"] != 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"微信接口错误: {data.get('errmsg', '未知错误')} (errcode: {data.get('errcode')})"
                )
            
            if "session_key" not in data:
                raise HTTPException(status_code=400, detail="未获取到 session_key")
            
            return data
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"请求微信接口失败: {e}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=502, detail=f"连接微信接口失败: {e}")


def _decrypt_phone(encrypted_data: str, iv: str, session_key: str) -> str:
    """解密手机号数据"""
    try:
        # Base64 解码
        encrypted_data_bytes = base64.b64decode(encrypted_data)
        session_key_bytes = base64.b64decode(session_key)
        iv_bytes = base64.b64decode(iv)
        
        # AES-128-CBC 解密
        cipher = AES.new(session_key_bytes, AES.MODE_CBC, iv_bytes)
        decrypted_bytes = cipher.decrypt(encrypted_data_bytes)
        
        # 去除 PKCS#7 填充
        decrypted_bytes = unpad(decrypted_bytes, 16)
        
        # 解析 JSON
        decrypted_data = json.loads(decrypted_bytes.decode('utf-8'))
        
        # 验证 watermark（可选，用于验证解密成功）
        watermark = decrypted_data.get("watermark", {})
        if watermark.get("appid") != settings.WX_APPID:
            raise HTTPException(status_code=400, detail="解密数据验证失败: appid 不匹配")
        
        # 获取手机号
        phone = decrypted_data.get("phoneNumber")
        if not phone:
            raise HTTPException(status_code=400, detail="解密数据中未找到手机号")
        
        return phone
    except base64.binascii.Error:
        raise HTTPException(status_code=400, detail="Base64 解码失败")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="解密数据 JSON 解析失败")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"解密失败: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解密过程出错: {str(e)}")


@router.post("/decrypt-phone", response_model=WxDecryptPhoneResponse)
@log_exceptions
async def decrypt_phone(payload: WxDecryptPhoneRequest):
    """
    获取微信小程序手机号
    
    支持两种方式：
    1. 新版本 API（基础库 2.21.2+）：phoneCode 是字符串 code，直接调用微信接口获取手机号
    2. 旧版本 API：phoneCode 是包含 encryptedData 和 iv 的对象，需要解密
    
    Args:
        payload: 包含 code 和 phoneCode 的请求体
            - code: 微信登录 code（通过 wx.login() 获取，新版本可能不需要）
            - phoneCode: 
              * 新版本：手机号授权 code（字符串）
              * 旧版本：包含 encryptedData 和 iv 的对象或 JSON 字符串
    
    Returns:
        解密后的手机号
    """
    print('>>>>phoneCode type:', type(payload.phoneCode), 'value:', payload.phoneCode)
    
    # 判断是新版本 API（phoneCode 是字符串 code）还是旧版本（包含 encryptedData 和 iv）
    if isinstance(payload.phoneCode, str):
        # 尝试解析 JSON，如果失败则认为是新版本的 code
        try:
            phone_code_data = json.loads(payload.phoneCode)
            # 如果能解析成 JSON，检查是否包含 encryptedData 和 iv
            if isinstance(phone_code_data, dict) and "encryptedData" in phone_code_data and "iv" in phone_code_data:
                # 旧版本：包含 encryptedData 和 iv
                encrypted_data = phone_code_data.get("encryptedData")
                iv = phone_code_data.get("iv")
                # 通过 code 获取 session_key
                session_data = await _get_session_key(payload.code)
                session_key = session_data["session_key"]
                # 解密手机号
                phone = _decrypt_phone(encrypted_data, iv, session_key)
            else:
                # 新版本：直接是 code，调用微信接口获取手机号
                phone = await _get_phone_by_code(payload.phoneCode)
        except json.JSONDecodeError:
            # 不是 JSON，认为是新版本的 code
            phone = await _get_phone_by_code(payload.phoneCode)
    elif isinstance(payload.phoneCode, dict):
        # 旧版本：直接是对象，包含 encryptedData 和 iv
        encrypted_data = payload.phoneCode.get("encryptedData")
        iv = payload.phoneCode.get("iv")
        
        if not encrypted_data or not iv:
            raise HTTPException(
                status_code=400,
                detail="phoneCode 格式错误: 必须包含 encryptedData 和 iv 字段"
            )
        
        # 通过 code 获取 session_key
        session_data = await _get_session_key(payload.code)
        session_key = session_data["session_key"]
        # 解密手机号
        phone = _decrypt_phone(encrypted_data, iv, session_key)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"phoneCode 格式错误: 必须是字符串或对象，当前类型: {type(payload.phoneCode).__name__}"
        )
    
    return JSONResponse(
        content={
            "message": "success",
            "data": {"phone": phone},
        },
        status_code=200,
    )
