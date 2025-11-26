from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.deps import get_db, get_db_lims
from models.sample import Sample
from schemas.sample import SampleCreate, SampleRead, SampleUpdate
from crud import sample as crud_sample
from common.decorators import log_exceptions
from api.routes.remote import _get_projects_data


router = APIRouter()


@router.get("/", response_model=list[SampleRead])
@log_exceptions
def list_samples(
    user_id: str | None = Query(None, description="用户ID"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Sample).order_by(Sample.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=SampleRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_sample(payload: SampleCreate, db: Session = Depends(get_db)):
    sample = crud_sample.create_sample(db, sample=payload)
    return sample

@router.get("/user_id", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_user_id(
    user_id: str = Query(..., description="用户ID"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return samples



@router.get("/phone", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_phone(
    phone: str = Query(..., description="手机号"),
    db: Session = Depends(get_db),
    db_lims: Session = Depends(get_db_lims),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    programEnums = _get_projects_data(db_lims)
    # print('>>>>programEnums', programEnums)
    # 创建 program_id 到 name 的映射字典
    program_map = {item.get('id'): item.get('name') for item in programEnums if item.get('id') is not None}
    print('>>>>program_map', program_map)
    samples = crud_sample.get_samples_by_phone(db, phone=phone, skip=skip, limit=limit)
    print('>>>>samples', samples, type(samples))
    # 强制转换为列表
    samples = list(samples) if samples else []
    print('>>>>samples after list()', samples, type(samples), len(samples))
    for sample in samples:
        try:
            # program_id 等字段现在已经是字符串类型（通过 BigIntegerAsString）
            print('>>>>sample program_id:', sample.program_id, type(sample.program_id))
            sample.program_name = program_map.get(sample.program_id)
        except Exception as e:
            print(f'>>>>error processing sample: {e}')
            continue
    return samples


@router.get("/id-number", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_id_number(
    id_number: str = Query(..., description="身份证号"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_id_number(db, id_number=id_number, skip=skip, limit=limit)
    return samples


@router.get("/user", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_user_id(
    user_id: str = Query(..., description="用户ID"),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return samples


@router.get("/{sample_id}", response_model=SampleRead)
@log_exceptions
def get_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = crud_sample.get_sample(db, sample_id=sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/{sample_id}/update", response_model=SampleRead)
@log_exceptions
def update_sample(sample_id: int, payload: SampleUpdate, db: Session = Depends(get_db)):
    sample = crud_sample.update_sample(db, sample_id=sample_id, sample=payload)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/{sample_id}/delete")
@log_exceptions
def delete_sample(sample_id: int, db: Session = Depends(get_db)):
    success = crud_sample.delete_sample(db, sample_id=sample_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sample not found")
    return None
