from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status

from app.schemas.user import UserCreate, UserRead


router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users():
    # 固定返回示例数据
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [
        {
            "id": 2,
            "email": "alice@example.com",
            "full_name": "Alice",
            "created_at": now,
        },
        {
            "id": 1,
            "email": "bob@example.com",
            "full_name": "Bob",
            "created_at": now,
        },
    ]


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate):
    # 不实际写库，直接回显一个固定 ID 的用户
    return {
        "id": 999,
        "email": payload.email,
        "full_name": payload.full_name,
        "created_at": datetime.now(timezone.utc),
    }


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int):
    # 固定返回，如果需要，可根据 ID 变化填充不同数据
    if user_id <= 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user_id,
        "email": "demo@example.com",
        "full_name": "Demo User",
        "created_at": datetime(2024, 1, 1, tzinfo=timezone.utc),
    }
