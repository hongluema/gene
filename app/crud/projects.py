from sqlalchemy.orm import Session
from models.projects import Project
from schemas.projects import ProjectCreate, ProjectUpdate
import random
import string


def generate_project_id(db: Session) -> str:
    """生成唯一的 project_id，格式为 'p' + 11位随机字符（总计12位）。"""
    while True:
        random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=11))
        project_id = f"p{random_chars}"
        if not db.query(Project).filter(Project.project_id == project_id).first():
            return project_id


def create_project(db: Session, project: ProjectCreate) -> Project:
    db_project = Project(
        project_id=generate_project_id(db),
        name=project.name,
        desc=project.desc,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_project(db: Session, project_id: str) -> Project | None:
    return db.query(Project).filter(Project.project_id == project_id).first()


def get_projects(db: Session, skip: int = 0, limit: int = 100) -> list[Project]:
    return db.query(Project).offset(skip).limit(limit).all()


def update_project(db: Session, project_id: str, project: ProjectUpdate) -> Project | None:
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not db_project:
        return None
    if project.name is not None:
        db_project.name = project.name
    if project.desc is not None:
        db_project.desc = project.desc
    db.commit()
    db.refresh(db_project)
    return db_project


def delete_project(db: Session, project_id: str) -> bool:
    db_project = db.query(Project).filter(Project.project_id == project_id).first()
    if not db_project:
        return False
    db.delete(db_project)
    db.commit()
    return True

