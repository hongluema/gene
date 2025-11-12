from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
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
        openid=user.openid,
        name=_normalize_empty_to_none(user.name),
        nickname=_normalize_empty_to_none(user.nickname),
        avatar=_normalize_empty_to_none(user.avatar),
        mobile=_normalize_empty_to_none(user.mobile),
        idCard=_normalize_empty_to_none(user.idCard),
        sex=user.sex,  # 已通过 Pydantic 校验枚举
        age=user.age,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_username(db: Session, nickname: str) -> User | None:
    return db.query(User).filter(User.nickname == nickname).first()


def get_user_by_openid(db: Session, openid: str) -> User | None:
    return db.query(User).filter(User.openid == openid).first()


def create_user_by_openid(db: Session, openid: str) -> User:
    """根据 openid 创建新用户，自动生成 user_id。"""
    db_user = User(
        user_id=generate_user_id(db),
        openid=openid,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
