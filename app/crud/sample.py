from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.sample import Sample
from schemas.sample import SampleCreate, SampleUpdate
import random
import string
from datetime import datetime


def generate_sample_id(db: Session) -> str:
    """生成唯一的 sample_id，格式为 6 + 17位随机数字（总计18位）。"""
    while True:
        random_digits = ''.join(random.choices(string.digits, k=17))
        sample_id = f"6{random_digits}"
        if not db.query(Sample).filter(Sample.sample_id == sample_id).first():
            return sample_id


def create_sample(db: Session, sample: SampleCreate) -> Sample:
    db_sample = Sample(
        sample_id=generate_sample_id(db),
        code=sample.code,
        name=sample.name,
        type=sample.type,
        process=sample.process,
        user_id=sample.user_id,
        phone=sample.phone,
        id_number=sample.id_number,
        gender=sample.gender,
        age=sample.age,
        program_id=sample.program_id,
        org_id=sample.org_id,
        sample_data_id=sample.sample_data_id,
        sample_data_name=sample.sample_data_name,
        order_id=sample.order_id,
        desc=sample.desc,
        # 新增字段，如果未提供则设为None
        receive_time=sample.receive_time,
        report_date=sample.report_date,
        test_user=sample.test_user,
        see_user=sample.see_user,
        mongoid=sample.mongoid,
        usable=sample.usable
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


def get_sample(db: Session, sample_id: str) -> Sample | None:
    return db.query(Sample).filter(Sample.sample_id == sample_id).first()


def get_sample_by_code(db: Session, code: str) -> Sample | None:
    return db.query(Sample).filter(Sample.code == code).first()


def get_samples(db: Session, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).offset(skip).limit(limit).all()


def get_samples_by_user(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).order_by(Sample.created_at.desc()).filter(Sample.user_id == user_id).offset(skip).limit(limit).all()


def get_samples_by_phone(db: Session, phone: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).order_by(Sample.created_at.desc()).filter(Sample.phone == phone).offset(skip).limit(limit).all()


def get_samples_by_id_number(db: Session, id_number: str, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).order_by(Sample.created_at.desc()).filter(Sample.id_number == id_number).offset(skip).limit(limit).all()


def get_samples_by_user_or_phone(db: Session, user_id: str, phone: str) -> list[Sample]:
    """根据 user_id 或 phone 查询 samples，条件为 phone = phone OR user_id = user_id，并去重"""
    samples = db.query(Sample).order_by(Sample.created_at.desc()).filter(
        or_(Sample.phone == phone, Sample.user_id == user_id)
    ).all()
    # 根据 sample_id 去重（使用字典保持顺序）
    seen = set()
    unique_samples = []
    for sample in samples:
        if sample.sample_id not in seen:
            seen.add(sample.sample_id)
            unique_samples.append(sample)
    return unique_samples


def get_samples_by_program(db: Session, program_id: int, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).filter(Sample.program_id == program_id).offset(skip).limit(limit).all()


def get_samples_by_org(db: Session, org_id: int, skip: int = 0, limit: int = 100) -> list[Sample]:
    return db.query(Sample).filter(Sample.org_id == org_id).offset(skip).limit(limit).all()


def update_sample(db: Session, sample_id: str, sample: SampleUpdate) -> Sample | None:
    db_sample = db.query(Sample).filter(Sample.sample_id == sample_id).first()
    if not db_sample:
        return None
    if sample.code is not None:
        db_sample.code = sample.code
    if sample.name is not None:
        db_sample.name = sample.name
    if sample.type is not None:
        db_sample.type = sample.type
    if sample.process is not None:
        db_sample.process = sample.process
    if sample.user_id is not None:
        db_sample.user_id = sample.user_id
    if sample.phone is not None:
        db_sample.phone = sample.phone
    if sample.id_number is not None:
        db_sample.id_number = sample.id_number
    if sample.gender is not None:
        db_sample.gender = sample.gender
    if sample.age is not None:
        db_sample.age = sample.age
    if sample.program_id is not None:
        db_sample.program_id = sample.program_id
    if sample.org_id is not None:
        db_sample.org_id = sample.org_id
    if sample.sample_data_id is not None:
        db_sample.sample_data_id = sample.sample_data_id
    if sample.sample_data_name is not None:
        db_sample.sample_data_name = sample.sample_data_name
    if sample.order_id is not None:
        db_sample.order_id = sample.order_id
    if sample.desc is not None:
        db_sample.desc = sample.desc
    # 新增字段更新
    if sample.receive_time is not None:
        db_sample.receive_time = sample.receive_time
    if sample.report_date is not None:
        db_sample.report_date = sample.report_date
    if sample.test_user is not None:
        db_sample.test_user = sample.test_user
    if sample.see_user is not None:
        db_sample.see_user = sample.see_user
    if sample.usable is not None:
        db_sample.usable = sample.usable
    db.commit()
    db.refresh(db_sample)
    return db_sample


def delete_sample(db: Session, sample_id: str) -> bool:
    db_sample = db.query(Sample).filter(Sample.sample_id == sample_id).first()
    if not db_sample:
        return None
    db_sample.usable = 0
    db.commit()
    db.refresh(db_sample)
    return True