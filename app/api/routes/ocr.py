import base64
from typing import Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from common.decorators import log_exceptions
from core.config import settings

# 导入阿里云 OCR SDK（基于官方文档）
try:
    from alibabacloud_ocr_api20210707.client import Client as OcrClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ocr_api20210707 import models as ocr_models
    from alibabacloud_tea_util import models as util_models
except ImportError:
    OcrClient = None
    print("Warning: alibabacloud_ocr_api20210707 not installed. Please install it with: pip install alibabacloud_ocr_api20210707")


router = APIRouter()


class IDCardOCRRequest(BaseModel):
    """身份证 OCR 请求模型（用于 base64 方式）"""
    image_base64: str
    side: str = "face"  # face: 正面(人像面), back: 背面(国徽面)


class IDCardOCRResponse(BaseModel):
    """身份证 OCR 响应模型"""
    success: bool
    message: str
    data: Optional[dict] = None


def _create_ocr_client() -> OcrClient:
    """
    创建阿里云 OCR 客户端（基于官方文档）
    官方文档：https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeidcard
    """
    if not OcrClient:
        raise HTTPException(
            status_code=500,
            detail="Aliyun OCR SDK not installed. Please install: pip install alibabacloud_ocr_api20210707"
        )

    if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Aliyun OCR credentials not configured. Please set ALIYUN_ACCESS_KEY_ID and ALIYUN_ACCESS_KEY_SECRET in .env file"
        )

    # 按照官方文档配置客户端
    config = open_api_models.Config(
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
    )
    # 设置 endpoint（必须，根据官方文档）
    config.endpoint = 'ocr-api.cn-hangzhou.aliyuncs.com'
    return OcrClient(config)


def _parse_id_card_face(result_data) -> dict:
    """
    解析身份证正面（人像面）信息
    根据 RecognizeIdcard API 响应字段解析
    """
    # 处理可能的属性访问方式（对象属性或字典）
    def safe_get(obj, attr, default=""):
        if hasattr(obj, attr):
            value = getattr(obj, attr, default)
            return value if value is not None else default
        elif isinstance(obj, dict):
            return obj.get(attr, default)
        return default

    return {
        "name": safe_get(result_data, "name"),  # 姓名
        "gender": safe_get(result_data, "sex"),  # 性别
        "nationality": safe_get(result_data, "nationality"),  # 民族
        "birth_date": safe_get(result_data, "birth"),  # 出生日期
        "address": safe_get(result_data, "address"),  # 住址
        "id_number": safe_get(result_data, "num"),  # 身份证号码
    }


def _parse_id_card_back(result_data) -> dict:
    """
    解析身份证背面（国徽面）信息
    根据 RecognizeIdcard API 响应字段解析
    """
    # 处理可能的属性访问方式（对象属性或字典）
    def safe_get(obj, attr, default=""):
        if hasattr(obj, attr):
            value = getattr(obj, attr, default)
            return value if value is not None else default
        elif isinstance(obj, dict):
            return obj.get(attr, default)
        return default

    start_date = safe_get(result_data, "start_date")
    end_date = safe_get(result_data, "end_date")
    valid_period = f"{start_date}-{end_date}" if start_date and end_date else safe_get(result_data, "valid_period")

    return {
        "issue_authority": safe_get(result_data, "issue"),  # 签发机关
        "valid_period": valid_period,  # 有效期限
        "start_date": start_date,  # 有效期开始日期
        "end_date": end_date,  # 有效期结束日期
    }


@router.post("/id-card/recognize", response_model=IDCardOCRResponse)
@log_exceptions
async def recognize_id_card_base64(request: IDCardOCRRequest):
    """
    识别身份证信息（接收 base64 编码的图片）

    基于阿里云官方文档实现：
    https://help.aliyun.com/zh/ocr/developer-reference/api-ocr-api-2021-07-07-recognizeidcard

    Args:
        request: 包含 base64 编码的身份证图片和面向（正面/背面）

    Returns:
        身份证识别结果

    Example request body:
        {
            "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
            "side": "face"  // "face" 表示正面, "back" 表示背面
        }
    """
    try:
        # 创建 OCR 客户端
        client = _create_ocr_client()

        # 处理 base64 编码（去掉 data:image/xxx;base64, 前缀）
        image_data = request.image_base64
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]

        # 将 base64 解码为二进制数据（根据官方文档，body 应该是二进制数据）
        try:
            image_binary = base64.b64decode(image_data)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid base64 image data: {str(e)}"
            )

        # 创建识别请求（根据官方文档）
        recognize_request = ocr_models.RecognizeIdcardRequest(
            body=image_binary  # body 接收二进制数据
        )

        # 创建运行时选项
        runtime = util_models.RuntimeOptions()

        # 调用阿里云 OCR API
        response = client.recognize_idcard_with_options(recognize_request, runtime)
        print('>>>>response', response)
        if not response or not response.body:
            raise HTTPException(
                status_code=500,
                detail="OCR service returned empty response"
            )

        # 解析响应数据
        result_data = response.body.Data
        print('>>>>result_data', result_data)
        if not result_data:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "No ID card detected in the image",
                    "data": None
                },
                status_code=200
            )

        # 根据正反面解析不同的字段
        if request.side == "face":
            parsed_data = _parse_id_card_face(result_data)
        else:  # back
            parsed_data = _parse_id_card_back(result_data)

        return JSONResponse(
            content={
                "success": True,
                "message": "ID card recognized successfully",
                "data": parsed_data
            },
            status_code=200
        )

    except HTTPException:
        raise
    except Exception as e:
        error_str = str(e)
        print(f">>>>OCR recognition failed: {repr(e)}")

        # 增强错误处理：明确提示不同的错误类型
        if "ocrServiceNotOpen" in error_str or ("401" in error_str and "not activated" in error_str.lower()):
            raise HTTPException(
                status_code=503,
                detail="OCR service not activated. Please activate Aliyun OCR service in your Aliyun console: https://www.aliyun.com/product/ocr"
            )
        elif "InvalidAccessKeyId" in error_str or "Specified access key is not found" in error_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid Aliyun Access Key ID. Please check your credentials."
            )
        elif "SignatureDoesNotMatch" in error_str:
            raise HTTPException(
                status_code=401,
                detail="Invalid Aliyun Access Key Secret. Please check your credentials."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to recognize ID card: {error_str}"
            )


@router.post("/id-card/recognize-file", response_model=IDCardOCRResponse)
@log_exceptions
async def recognize_id_card_file(
    file: UploadFile = File(..., description="身份证图片文件"),
    side: str = Form("face", description="身份证面向: face(正面) 或 back(背面)")
):
    """
    识别身份证信息（接收文件上传）

    Args:
        file: 身份证图片文件
        side: 身份证面向，face 表示正面（人像面），back 表示背面（国徽面）

    Returns:
        身份证识别结果
    """
    try:
        # 读取文件内容
        file_content = await file.read()

        # 将文件内容转换为 base64
        image_base64 = base64.b64encode(file_content).decode('utf-8')

        # 调用 base64 识别接口
        request = IDCardOCRRequest(image_base64=image_base64, side=side)
        return await recognize_id_card_base64(request)

    except HTTPException:
        raise
    except Exception as e:
        print(f">>>>File upload OCR failed: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process uploaded file: {str(e)}"
        )


@router.get("/health")
@log_exceptions
async def health_check():
    """OCR 服务健康检查"""
    try:
        # 检查配置是否完整
        if not settings.ALIYUN_ACCESS_KEY_ID or not settings.ALIYUN_ACCESS_KEY_SECRET:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Aliyun OCR credentials not configured"
                },
                status_code=200
            )

        # 检查 SDK 是否已安装
        if not OcrClient:
            return JSONResponse(
                content={
                    "status": "error",
                    "message": "Aliyun OCR SDK not installed"
                },
                status_code=200
            )

        return JSONResponse(
            content={
                "status": "healthy",
                "message": "OCR service is running",
                "endpoint": "ocr-api.cn-hangzhou.aliyuncs.com"
            },
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "error",
                "message": f"Health check failed: {str(e)}"
            },
            status_code=200
        )
