from sqlalchemy.orm import Session
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
import random
import string


def generate_organization_id(db: Session) -> str:
    """生成唯一的 organization_id，格式为 'o' + 11位随机字符（总计12位）。"""
    while True:
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        organization_id = f"o{random_chars}"
        if not db.query(Organization).filter(Organization.organization_id == organization_id).first():
            return organization_id


def create_organization(db: Session, organization: OrganizationCreate) -> Organization:
    db_organization = Organization(
        organization_id=generate_organization_id(db),
        name=organization.name,
        desc=organization.desc,
    )
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization


def get_organization(db: Session, organization_id: str) -> Organization | None:
    return db.query(Organization).filter(Organization.organization_id == organization_id).first()


def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organization]:
    return db.query(Organization).offset(skip).limit(limit).all()


def update_organization(db: Session, organization_id: str, organization: OrganizationUpdate) -> Organization | None:
    db_organization = db.query(Organization).filter(Organization.organization_id == organization_id).first()
    if not db_organization:
        return None
    if organization.name is not None:
        db_organization.name = organization.name
    if organization.desc is not None:
        db_organization.desc = organization.desc
    db.commit()
    db.refresh(db_organization)
    return db_organization


def delete_organization(db: Session, organization_id: str) -> bool:
    db_organization = db.query(Organization).filter(Organization.organization_id == organization_id).first()
    if not db_organization:
        return False
    db.delete(db_organization)
    db.commit()
    return True

