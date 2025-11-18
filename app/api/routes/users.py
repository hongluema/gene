from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.crud import user as crud_user


from app.common.decorators import log_exceptions


router = APIRouter()


@router.get("/", response_model=list[UserRead])
@log_exceptions
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/create", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = crud_user.create_user(db, user=payload)
    return user


@router.get("/{user_id}", response_model=UserRead)
@log_exceptions
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/update", response_model=UserRead)
@log_exceptions
def update_user(user_id: str, payload: UserUpdate, db: Session = Depends(get_db)):
    user = crud_user.update_user(db, user_id=user_id, user=payload)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/{user_id}/delete")
@log_exceptions
def delete_user(user_id: str, db: Session = Depends(get_db)):
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return None
