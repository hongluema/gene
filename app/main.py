from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import api_router
from app.db.base import engine, Base


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 无数据库模式：不执行建表或连接
    yield

# 创建所有模型对应的表（如果表不存在）
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(api_router)


@app.get("/health", tags=["health"])  # Simple root-level health endpoint
def health():
    return {"status": "ok"}