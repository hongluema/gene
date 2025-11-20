from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_db
from models.organization import Organization
from schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from crud import organization as crud_organization
from common.decorators import log_exceptions


router = APIRouter()


@router.get("/", response_model=list[OrganizationRead])
@log_exceptions
def list_organizations(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Organization).order_by(Organization.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    organization = crud_organization.create_organization(db, organization=payload)
    return organization


@router.get("/{org_id}", response_model=OrganizationRead)
@log_exceptions
def get_organization(org_id: int, db: Session = Depends(get_db)):
    organization = crud_organization.get_organization(db, org_id=org_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/{org_id}/update", response_model=OrganizationRead)
@log_exceptions
def update_organization(org_id: int, payload: OrganizationUpdate, db: Session = Depends(get_db)):
    organization = crud_organization.update_organization(db, org_id=org_id, organization=payload)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/{org_id}/delete")
@log_exceptions
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    success = crud_organization.delete_organization(db, org_id=org_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return None
