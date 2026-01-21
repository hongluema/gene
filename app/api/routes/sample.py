from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from api.deps import get_db, get_db_lims
from models.sample import Sample
from models.apply import Apply
from schemas.sample import SampleCreate, SampleRead, SampleUpdate
from crud import sample as crud_sample
from common.decorators import log_exceptions
from api.routes.remote import _get_projects_data, _get_organizations_data


router = APIRouter()


def _enrich_samples_with_apply_status(samples, db: Session, filter_approved: bool = False) -> list[Sample]:
    """为 samples 列表中的每个 sample 添加 apply_status 字段，并可选择过滤掉 approved 状态的样本

    Args:
        samples: 样本列表
        db: 数据库会话
        filter_approved: 是否过滤掉 status 为 approved 的样本

    Returns:
        处理后的样本列表
    """
    if not samples:
        return samples

    # 查询 applies 表获取 apply_status（usable=1 会自动过滤）
    sample_ids = [sample.sample_id for sample in samples]
    apply_map = {}
    if sample_ids:
        applies = db.query(Apply).filter(Apply.sample_id.in_(sample_ids)).all()
        apply_map = {apply.sample_id: apply.status for apply in applies}

    # 为每个 sample 添加 apply_status 属性
    for sample in samples:
        sample.apply_status = apply_map.get(sample.sample_id)

    # 过滤掉 status 为 approved 的样本（如果需要）
    if filter_approved:
        samples = [sample for sample in samples if sample.apply_status != 'approved']

    return samples


def _enrich_samples_with_program_name(samples, db_lims: Session) -> list[Sample]:
    """为 samples 列表中的每个 sample 添加 program_name 字段"""
    programEnums = _get_projects_data(db_lims)
    organizations = _get_organizations_data(db_lims)
    organization_map = {item.get('id'): item.get('name') for item in organizations if item.get('id') is not None}
    print('>>>>organization_map', organization_map)
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
            print('>>>>sample org_id:', sample.org_id, organization_map.get(sample.org_id))
            organization_name = organization_map.get(str(sample.org_id))
            sample.organization_name = organization_name
            print('>>>>sample organization_name:', sample.organization_name)
        except Exception as e:
            print(f'>>>>error processing sample: {e}')
            continue
    return samples


@router.get("/list", response_model=list[SampleRead])
@log_exceptions
def list_samples(
    user_id: str | None = Query(None, description="用户ID"),
    sample_id: str | None = Query(None, description="样品ID"),
    name: str | None = Query(None, description="检测人姓名"),
    id_number: str | None = Query(None, description="身份证号"),
    phone: str | None = Query(None, description="手机号"),
    program_name: str | None = Query(None, description="项目名称"),
    status: str | None = Query(None, description="样本状态(waiting/progressing/progressed)"),
    start_time: str | None = Query(None, description="开始时间(YYYY-MM-DD)"),
    end_time: str | None = Query(None, description="结束时间(YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    db_lims: Session = Depends(get_db_lims),
    begin: int = Query(0, ge=0),
    length: int = Query(20, ge=1, le=100),
):
    from datetime import datetime

    # 统一使用 ORM 方式查询，确保自动应用 usable=1 条件
    query = db.query(Sample)
    count_query = db.query(Sample)

    # 筛选条件
    if sample_id:
        query = query.filter(Sample.sample_id.like(f"%{sample_id}%"))
        count_query = count_query.filter(Sample.sample_id.like(f"%{sample_id}%"))
    if name:
        query = query.filter(Sample.name.like(f"%{name}%"))
        count_query = count_query.filter(Sample.name.like(f"%{name}%"))
    if id_number:
        query = query.filter(Sample.id_number.like(f"%{id_number}%"))
        count_query = count_query.filter(Sample.id_number.like(f"%{id_number}%"))
    if phone:
        query = query.filter(Sample.phone.like(f"%{phone}%"))
        count_query = count_query.filter(Sample.phone.like(f"%{phone}%"))
    if status:
        query = query.filter(Sample.process == status)
        count_query = count_query.filter(Sample.process == status)
    if start_time:
        start_dt = datetime.strptime(start_time, "%Y-%m-%d")
        query = query.filter(Sample.created_at >= start_dt)
        count_query = count_query.filter(Sample.created_at >= start_dt)
    if end_time:
        end_dt = datetime.strptime(end_time, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        query = query.filter(Sample.created_at <= end_dt)
        count_query = count_query.filter(Sample.created_at <= end_dt)

    # 如果有 program_name 筛选，先获取对应的 program_id
    if program_name:
        programEnums = _get_projects_data(db_lims)
        matching_program_ids = [str(item.get('id')) for item in programEnums if item.get('name') and program_name in item.get('name')]
        if matching_program_ids:
            query = query.filter(Sample.program_id.in_(matching_program_ids))
            count_query = count_query.filter(Sample.program_id.in_(matching_program_ids))
        else:
            # 没有匹配的项目，返回空结果
            return JSONResponse(content={"message": "success", "data": {"list": [], "total": 0}}, status_code=200)

    query = query.order_by(Sample.created_at.desc())
    samples = query.offset(begin).limit(length).all()

    # 添加 apply_status 属性（不过滤）
    samples = _enrich_samples_with_apply_status(samples, db, filter_approved=False)

    total = count_query.count()
    sample_data = _enrich_samples_with_program_name(samples, db_lims)
    print('>>>>sample_data', sample_data)
    # 将sample_data 转为 list
    sample_data = [SampleRead.model_validate(sample).model_dump(mode='json') for sample in sample_data]
    return JSONResponse(content={"message": "success", "data": {"list": sample_data, "total": total}}, status_code=200)


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

    # 添加 apply_status 属性并过滤掉 approved 状态的样本
    samples = _enrich_samples_with_apply_status(samples, db, filter_approved=True)

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

    # 添加 apply_status 属性并过滤掉 approved 状态的样本
    samples = _enrich_samples_with_apply_status(samples, db, filter_approved=True)

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

    # 添加 apply_status 属性并过滤掉 approved 状态的样本
    samples = _enrich_samples_with_apply_status(samples, db, filter_approved=True)

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
        return JSONResponse(
            content={"message": "样本不存在", "data": {"sample_id": payload.sample_id}, "success": False},
            status_code=400,
        )
    return JSONResponse(
            content={"message": "更新成功", "data": {"sample_id": payload.sample_id}, "success": True},
            status_code=200,
        )


@router.post("/{sample_id}/delete")
@log_exceptions
def delete_sample(sample_id: str, db: Session = Depends(get_db)):
    success = crud_sample.delete_sample(db, sample_id=sample_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sample not found")
    return None

