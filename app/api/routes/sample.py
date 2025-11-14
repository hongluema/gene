from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.sample import Sample
from app.schemas.sample import SampleCreate, SampleRead, SampleUpdate
from app.crud import sample as crud_sample


router = APIRouter()


@router.get("/", response_model=list[SampleRead])
def list_samples(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Sample).order_by(Sample.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=SampleRead, status_code=status.HTTP_201_CREATED)
def create_sample(payload: SampleCreate, db: Session = Depends(get_db)):
    sample = crud_sample.create_sample(db, sample=payload)
    return sample


@router.get("/{sample_id}", response_model=SampleRead)
def get_sample(sample_id: int, db: Session = Depends(get_db)):
    sample = crud_sample.get_sample(db, sample_id=sample_id)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/{sample_id}/update", response_model=SampleRead)
def update_sample(sample_id: int, payload: SampleUpdate, db: Session = Depends(get_db)):
    sample = crud_sample.update_sample(db, sample_id=sample_id, sample=payload)
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return sample


@router.post("/{sample_id}/delete")
def delete_sample(sample_id: int, db: Session = Depends(get_db)):
    success = crud_sample.delete_sample(db, sample_id=sample_id)
    if not success:
        raise HTTPException(status_code=404, detail="Sample not found")
    return None
