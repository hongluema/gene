from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.crud import organization as crud_organization


router = APIRouter()


@router.get("/", response_model=list[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Organization).order_by(Organization.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    organization = crud_organization.create_organization(db, organization=payload)
    return organization


@router.get("/{organization_id}", response_model=OrganizationRead)
def get_organization(organization_id: str, db: Session = Depends(get_db)):
    organization = crud_organization.get_organization(db, organization_id=organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/{organization_id}/update", response_model=OrganizationRead)
def update_organization(organization_id: str, payload: OrganizationUpdate, db: Session = Depends(get_db)):
    organization = crud_organization.update_organization(db, organization_id=organization_id, organization=payload)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    return organization


@router.post("/{organization_id}/delete")
def delete_organization(organization_id: str, db: Session = Depends(get_db)):
    success = crud_organization.delete_organization(db, organization_id=organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Organization not found")
    return None
