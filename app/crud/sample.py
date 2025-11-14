from sqlalchemy.orm import Session
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleUpdate
import random
import string


def generate_sample_id(db: Session) -> str:
    """生成唯一的 sample_id，格式为 's' + 11位随机字符（总计12位）。"""
    while True:
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        sample_id = f"s{random_chars}"
        if not db.query(Sample).filter(Sample.sample_id == sample_id).first():
            return sample_id


def create_sample(db: Session, sample: SampleCreate) -> Sample:
    db_sample = Sample(
        sample_id=generate_sample_id(db),
        sample_number=sample.sample_number,
        name=sample.name,
        type=sample.type,
        process=sample.process,
        user_id=sample.user_id,
        project_id=sample.project_id,
        organization_id=sample.organization_id,
        desc=sample.desc,
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def get_sample(db: Session, sample_id: str) -> Sample | None:
    return db.query(Sample).filter(Sample.sample_id == sample_id).first()


def get_sample_by_number(db: Session, sample_number: str) -> Sample | None:
    return db.query(Sample).filter(Sample.sample_number == sample_number).first()


def get_samples(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).offset(skip).limit(limit).all()


def get_samples_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).filter(Sample.user_id == user_id).offset(skip).limit(limit).all()


def get_samples_by_project(db: Session, project_id: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).filter(Sample.project_id == project_id).offset(skip).limit(limit).all()


def get_samples_by_organization(db: Session, organization_id: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).filter(Sample.organization_id == organization_id).offset(skip).limit(limit).all()


def update_sample(db: Session, sample_id: str, sample: SampleUpdate) -> Sample | None:
    db_sample = db.query(Sample).filter(Sample.sample_id == sample_id).first()
    if not db_sample:
        return None
    if sample.code is not None:
        db_sample.sample_number = sample.code
    if sample.name is not None:
        db_sample.name = sample.name
    if sample.type is not None:
        db_sample.type = sample.type
    if sample.process is not None:
        db_sample.process = sample.process
    if sample.user_id is not None:
        db_sample.user_id = sample.user_id
    if sample.project_id is not None:
        db_sample.project_id = sample.project_id
    if sample.organization_id is not None:
        db_sample.organization_id = sample.organization_id
    if sample.desc is not None:
        db_sample.desc = sample.desc
    db.commit()
    db.refresh(db_sample)
    return db_sample


def delete_sample(db: Session, sample_id: str) -> bool:
    db_sample = db.query(Sample).filter(Sample.sample_id == sample_id).first()
    if not db_sample:
        return False
    db.delete(db_sample)
    db.commit()
    return True

