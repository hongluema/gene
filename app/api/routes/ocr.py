import base64
from typing import Optional
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from common.decorators import log_exceptions
from core.config import settings

# 导入阿里云 OCR SDK
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
    """创建阿里云 OCR 客户端"""
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

    config = open_api_models.Config(
        access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
        access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET,
        endpoint='ocr.cn-shanghai.aliyuncs.com'
    )
    return OcrClient(config)


def _parse_id_card_face(data: dict) -> dict:
    """解析身份证正面（人像面）信息"""
    return {
        "name": data.get("name", ""),  # 姓名
        "gender": data.get("sex", ""),  # 性别
        "nationality": data.get("nationality", ""),  # 民族
        "birth_date": data.get("birth", ""),  # 出生日期
        "address": data.get("address", ""),  # 住址
        "id_number": data.get("num", ""),  # 身份证号码
    }


def _parse_id_card_back(data: dict) -> dict:
    """解析身份证背面（国徽面）信息"""
    return {
        "issue_authority": data.get("issue", ""),  # 签发机关
        "valid_period": data.get("valid_period", ""),  # 有效期限
        "start_date": data.get("start_date", ""),  # 有效期开始日期
        "end_date": data.get("end_date", ""),  # 有效期结束日期
    }


@router.post("/id-card/recognize", response_model=IDCardOCRResponse)
@log_exceptions
async def recognize_id_card_base64(request: IDCardOCRRequest):
    """
    识别身份证信息（接收 base64 编码的图片）

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

        # 创建识别请求
        recognize_request = ocr_models.RecognizeIdcardRequest(
            body=image_data.encode('utf-8')
        )
        print('>>>>recognize_request', recognize_request)
        runtime = util_models.RuntimeOptions()

        # 调用阿里云 OCR API
        response = client.recognize_idcard_with_options(recognize_request, runtime)
        print('>>>>response', response)
        if not response or not response.body:
            raise HTTPException(status_code=500, detail="OCR service returned empty response")

        # 解析响应数据
        result_data = response.body.data

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
            parsed_data = _parse_id_card_face({
                "name": result_data.get("name"),
                "sex": result_data.get("sex"),
                "nationality": result_data.get("nationality"),
                "birth": result_data.get("birth"),
                "address": result_data.get("address"),
                "num": result_data.get("num"),
            })
        else:  # back
            parsed_data = _parse_id_card_back({
                "issue": result_data.get("issue"),
                "valid_period": result_data.get("start_date") + "-" + result_data.get("end_date") if result_data.get("start_date") and result_data.get("end_date") else "",
                "start_date": result_data.get("start_date"),
                "end_date": result_data.get("end_date"),
            })

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
        print(f">>>>OCR recognition failed: {repr(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to recognize ID card: {str(e)}"
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
                "message": "OCR service is running"
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
