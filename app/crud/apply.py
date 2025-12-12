from sqlalchemy.orm import Session
from models.apply import Apply
from schemas.apply import ApplyCreate, ApplyUpdate, ApplyReview
import random
import string
from datetime import datetime


def generate_apply_id(db: Session) -> str:
    """生成唯一的 apply_id，格式为 'a' + 11位随机字符（总计12位）。"""
    while True:
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        apply_id = f"a{random_chars}"
        if not db.query(Apply).filter(Apply.apply_id == apply_id).first():
            return apply_id


def create_apply(db: Session, apply: ApplyCreate) -> Apply:
    """创建申请"""
    db_apply = Apply(
        apply_id=generate_apply_id(db),
        apply_user_id=apply.apply_user_id,
        apply_user_phone=apply.apply_user_phone,
        sample_id=apply.sample_id,
        type=apply.type,
        reason=apply.reason,
        status="pending"  # 默认状态为待审批
    )
    db.add(db_apply)
    db.commit()
    db.refresh(db_apply)
    return db_apply


def get_apply(db: Session, sample_id: str) -> Apply | None:
    """根据apply_id获取申请"""
    return db.query(Apply).filter(Apply.sample_id == sample_id).first()


def get_applies(db: Session, skip: int = 0, limit: int = 100) -> list[Apply]:
    """获取申请列表"""
    return db.query(Apply).order_by(Apply.created_at.desc()).offset(skip).limit(limit).all()


def get_applies_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[Apply]:
    """根据申请人获取申请列表"""
    return db.query(Apply).filter(Apply.apply_user_id == user_id).order_by(Apply.created_at.desc()).offset(skip).limit(limit).all()


def get_applies_by_sample(db: Session, sample_id: str, skip: int = 0, limit: int = 100) -> list[Apply]:
    """根据样本ID获取申请列表"""
    return db.query(Apply).filter(Apply.sample_id == sample_id).order_by(Apply.created_at.desc()).offset(skip).limit(limit).all()


def get_applies_by_status(db: Session, status: str, skip: int = 0, limit: int = 100) -> list[Apply]:
    """根据状态获取申请列表"""
    return db.query(Apply).filter(Apply.status == status).order_by(Apply.created_at.desc()).offset(skip).limit(limit).all()


def update_apply(db: Session, apply_id: str, apply: ApplyUpdate) -> Apply | None:
    """更新申请（仅限待审批状态）"""
    db_apply = db.query(Apply).filter(Apply.apply_id == apply_id).first()
    if not db_apply:
        return None
    # 只有待审批状态的申请可以被更新
    if db_apply.status != "pending":
        return None
    if apply.apply_user_phone is not None:
        db_apply.apply_user_phone = apply.apply_user_phone
    if apply.reason is not None:
        db_apply.reason = apply.reason
    db.commit()
    db.refresh(db_apply)
    return db_apply


def review_apply(db: Session, apply_review: ApplyReview) -> Apply | None:
    """审批申请"""
    db_apply = db.query(Apply).filter(Apply.apply_id == apply_review.apply_id).first()
    if not db_apply:
        return None
    # 只有待审批状态的申请可以被审批
    if db_apply.status != "pending":
        return None
    db_apply.status = apply_review.status
    db_apply.reviewer_id = apply_review.reviewer_id
    db_apply.review_time = datetime.now()
    db_apply.review_comment = apply_review.review_comment
    db.commit()
    db.refresh(db_apply)
    return db_apply


def delete_apply(db: Session, apply_id: str) -> bool:
    """删除申请（逻辑删除）"""
    db_apply = db.query(Apply).filter(Apply.apply_id == apply_id).first()
    if not db_apply:
        return None
    db_apply.usable = 0
    db.commit()
    db.refresh(db_apply)
    return True
