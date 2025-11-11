# 依赖项：获取数据库会话（每次请求创建一个会话，结束后关闭）
from app.db.base import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()