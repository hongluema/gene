from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.middleware.response_wrapper import UnifiedResponseMiddleware

from app.core.config import settings
from app.api.routes import api_router
from app.db.base import SessionLocal, engine, Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 无数据库模式：不执行建表或连接
    yield

# 创建所有模型对应的表（如果表不存在）
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS - 允许所有跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=False,  # 使用 "*" 时 credentials 必须为 False
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 统一响应中间件：将响应改为 {data, message, status_code}
app.add_middleware(UnifiedResponseMiddleware)

# Routers (prefix all routes with /api)
app.include_router(api_router, prefix="/api")


@app.get("/api/health", tags=["health"])  # Prefixed health endpoint
def health():
    return {"status": "ok"}
