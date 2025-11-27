from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_db
from models import User
from schemas.user import UserCreate, UserRead, UserUpdate
from crud import user as crud_user


from common.decorators import log_exceptions


router = APIRouter()


@router.get("/list", response_model=list[UserRead])
@log_exceptions
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    users = list(db.scalars(stmt))
    user_data = [UserRead.model_validate(user).model_dump(mode='json') for user in users]
    total = db.query(User).count()
    return JSONResponse(content={"message": "success", "data": {"list": user_data, "total": total}}, status_code=200)


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # If phone provided, check existence first
    if payload.phone:
        existed = db.query(User).filter(User.phone == payload.phone).first()
        if existed:
            return JSONResponse(
                content={"message": "用户已经存在", "data": {"user_id": existed.user_id, "id_number": existed.id_number}},
                status_code=200,
            )

    user = crud_user.create_user(db, user=payload)
    return user


@router.get("/info", response_model=UserRead)
@log_exceptions
def get_user(user_id: str = Query(..., description="用户ID"), db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/update", response_model=UserRead)
@log_exceptions
def update_user(payload: UserUpdate, db: Session = Depends(get_db)):
    print('>>>>>payload', payload);
    user = crud_user.update_user(db, user_id=payload.user_id, user=payload)
    if not user:
        return JSONResponse(
            content={"message": "用户不存在", "data": {"user_id": payload.user_id}},
            status_code=200,
        )
    return user


@router.post("/{user_id}/delete")
@log_exceptions
def delete_user(user_id: str, db: Session = Depends(get_db)):
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
