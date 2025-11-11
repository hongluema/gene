from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate  # 后面会定义 Pydantic 模型

# 创建用户
def create_user(db: Session, user: UserCreate):
    db_user = User(
        nickname=user.nickname,
        mobile=user.mobile,
        avatar=user.avatar
    )
    db.add(db_user)
    db.commit()  # 提交事务
    db.refresh(db_user)  # 刷新数据，获取数据库生成的 ID 等
    return db_user

# 查询用户（按 ID）
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

# 查询用户（按用户名）
def get_user_by_username(db: Session, nickname: str):
    return db.query(User).filter(User.nickname == nickname).first()