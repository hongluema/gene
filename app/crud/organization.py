from sqlalchemy.orm import Session
from models.organization import Organization
from schemas.organization import OrganizationCreate, OrganizationUpdate


def create_organization(db: Session, organization: OrganizationCreate) -> Organization:
    db_organization = Organization(
        name=organization.name,
        desc=organization.desc,
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_organization(db: Session, org_id: int) -> Organization | None:
    return db.query(Organization).filter(Organization.org_id == org_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organization]:
    return db.query(Organization).offset(skip).limit(limit).all()


def update_organization(db: Session, org_id: int, organization: OrganizationUpdate) -> Organization | None:
    db_organization = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not db_organization:
        return None
    if organization.name is not None:
        db_organization.name = organization.name
    if organization.desc is not None:
        db_organization.desc = organization.desc
    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, org_id: int) -> bool:
    db_organization = db.query(Organization).filter(Organization.org_id == org_id).first()
    if not db_organization:
        return False
    db.delete(db_organization)
    db.commit()
    return True

