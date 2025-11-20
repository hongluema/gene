from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate, UserUpdate
import random
import string


def _normalize_empty_to_none(value):
    if value is None:
        return None
    v = value.strip()
    return v if v != "" else None


def generate_user_id(db: Session) -> str:
    """生成唯一的 user_id，格式为 'u' + 11位随机字符（总计12位）。"""
    while True:
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        user_id = f"u{random_chars}"
        if not db.query(User).filter(User.user_id == user_id).first():
            return user_id


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(
        user_id=generate_user_id(db),
        name=_normalize_empty_to_none(user.name),
        avatar=_normalize_empty_to_none(user.avatar),
        phone=_normalize_empty_to_none(user.phone),
        id_number=_normalize_empty_to_none(user.id_number),
        gender=user.gender,  # 已通过 Pydantic 校验枚举
        age=user.age,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update_user(db: Session, user_id: str, user: UserUpdate) -> User | None:
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return None
    if user.name is not None:
        db_user.name = _normalize_empty_to_none(user.name)
    if user.avatar is not None:
        db_user.avatar = _normalize_empty_to_none(user.avatar)
    if user.phone is not None:
        db_user.phone = _normalize_empty_to_none(user.phone)
    if user.id_number is not None:
        db_user.id_number = _normalize_empty_to_none(user.id_number)
    if user.gender is not None:
        db_user.gender = user.gender
    if user.age is not None:
        db_user.age = user.age
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str) -> bool:
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True
