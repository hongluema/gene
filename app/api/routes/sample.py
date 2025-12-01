from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.deps import get_db, get_db_lims
from models.sample import Sample
from schemas.sample import SampleCreate, SampleRead, SampleUpdate
from crud import sample as crud_sample
from common.decorators import log_exceptions
from api.routes.remote import _get_projects_data


router = APIRouter()


def _enrich_samples_with_program_name(samples, db_lims: Session) -> list[Sample]:
    """为 samples 列表中的每个 sample 添加 program_name 字段"""
    programEnums = _get_projects_data(db_lims)
    # 创建 program_id 到 name 的映射字典
    program_map = {item.get('id'): item.get('name') for item in programEnums if item.get('id') is not None}
    print('>>>>program_map', program_map)
    # 强制转换为列表
    samples = list(samples) if samples else []
    print('>>>>samples after list()', samples, type(samples), len(samples))
    for sample in samples:
        try:
            # program_id 等字段现在已经是字符串类型（通过 BigIntegerAsString）
            print('>>>>sample program_id:', sample.program_id, program_map.get(str(sample.program_id)))
            program_name = program_map.get(str(sample.program_id))
            sample.program_name = program_name
        except Exception as e:
            print(f'>>>>error processing sample: {e}')
            continue
    return samples


@router.get("/list", response_model=list[SampleRead])
@log_exceptions
def list_samples(
    user_id: str | None = Query(None, description="用户ID"),
    db: Session = Depends(get_db),
    begin: int = Query(0, ge=0),
    length: int = Query(20, ge=1, le=100),
):
    # 统一使用 ORM 方式查询，确保自动应用 usable=1 条件
    query = db.query(Sample).order_by(Sample.created_at.desc())
    # if user_id:
    #     query = query.filter(Sample.user_id == user_id)
    samples = query.offset(begin).limit(length).all()
    sample_data = [SampleRead.model_validate(sample).model_dump(mode='json') for sample in samples]
    # user_data = [UserRead.model_validate(user).model_dump(mode='json') for user in users]
    # print('>>>>>user_data', user_data);
    total = db.query(Sample).count()
    return JSONResponse(content={"message": "success", "data": {"list": sample_data, "total": total}}, status_code=200)
    # return {"list": samples, "total": total}


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
    db_lims: Session = Depends(get_db_lims),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_user(db, user_id=user_id, skip=skip, limit=limit)
    print('>>>>samples', samples, type(samples))
    return _enrich_samples_with_program_name(samples, db_lims)



@router.get("/phone", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_phone(
    phone: str = Query(..., description="手机号"),
    db: Session = Depends(get_db),
    db_lims: Session = Depends(get_db_lims),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_phone(db, phone=phone, skip=skip, limit=limit)
    print('>>>>samples', samples, type(samples))
    return _enrich_samples_with_program_name(samples, db_lims)


@router.get("/id-number", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_id_number(
    id_number: str = Query(..., description="身份证号"),
    db: Session = Depends(get_db),
    db_lims: Session = Depends(get_db_lims),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_id_number(db, id_number=id_number, skip=skip, limit=limit)
    print('>>>>samples', samples, type(samples))
    return _enrich_samples_with_program_name(samples, db_lims)


@router.get("/query/my", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_user_or_phone(
    user_id: str = Query(..., description="用户ID"),
    phone: str = Query(..., description="手机号"),
    db: Session = Depends(get_db),
    db_lims: Session = Depends(get_db_lims),
):
    """根据 user_id 或 phone 查询 samples，条件为 phone = phone OR user_id = user_id，并去重"""
    samples = crud_sample.get_samples_by_user_or_phone(db, user_id=user_id, phone=phone)
    print('>>>>samples', samples, type(samples))
    return _enrich_samples_with_program_name(samples, db_lims)


@router.get("/{sample_id}", response_model=SampleRead)
@log_exceptions
def get_sample(sample_id: str, db: Session = Depends(get_db)):
    sample = crud_sample.get_sample(db, sample_id=sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/update", response_model=SampleRead)
@log_exceptions
def update_sample(payload: SampleUpdate, db: Session = Depends(get_db)):
    sample = crud_sample.update_sample(db, sample_id=payload.sample_id, sample=payload)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/{sample_id}/delete")
@log_exceptions
def delete_sample(sample_id: str, db: Session = Depends(get_db)):
    success = crud_sample.delete_sample(db, sample_id=sample_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sample not found")
    return None

