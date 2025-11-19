from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleRead, SampleUpdate
from app.crud import sample as crud_sample
from app.common.decorators import log_exceptions


router = APIRouter()


@router.get("/", response_model=list[SampleRead])
@log_exceptions
def list_samples(
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


@router.get("/phone/{phone}", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_phone(
    phone: str,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    samples = crud_sample.get_samples_by_phone(db, phone=phone, skip=skip, limit=limit)
    return samples


@router.get("/id-number/{id_number}", response_model=list[SampleRead])
@log_exceptions
def get_samples_by_id_number(
    id_number: str,
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
