from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.crud import user as crud_user
from app.db.base import SessionLocal
from app.schemas.user import UserCreate, UserRead

# 依赖项：获取数据库会话（每次请求创建一个会话，结束后关闭）
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/", response_model=list[UserRead])
def list_users():
    # 固定返回示例数据
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "id": 2,
            "mobile": "18212312312",
            "nickname": "Alice",
            "created_at": now,
        },
        {
            "id": 1,
            "mobile": "18212312312",
            "nickname": "Bob",
            "created_at": now,
        },
    ]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    # 不实际写库，直接回显一个固定 ID 的用户
    return {
        "id": 999,
        "mobile": payload.mobile,
        "nickname": payload.nickname,
        "created_at": datetime.now(timezone.utc),
    }


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud_user.get_user(db, user_id=user_id)
    # 固定返回，如果需要，可根据 ID 变化填充不同数据
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": db_user.id,
        "mobile": db_user.mobile,
        "nickname": db_user.nickname,
        "created_at": db_user.created_at,
    }
