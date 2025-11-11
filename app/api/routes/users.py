from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.crud import user as crud_user


router = APIRouter()


@router.get("/", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(User).order_by(User.id.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = crud_user.create_user(db, user=payload)
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mobile already exists")
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if payload.mobile is not None:
        user.mobile = payload.mobile
    if payload.avatar is not None:
        user.avatar = payload.avatar
    if payload.nickname is not None:
        user.nickname = payload.nickname

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Mobile already exists")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None
