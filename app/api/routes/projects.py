from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from api.deps import get_db
from models.projects import Project
from schemas.projects import ProjectCreate, ProjectRead, ProjectUpdate
from crud import projects as crud_project
from common.decorators import log_exceptions


router = APIRouter()


@router.get("/", response_model=list[ProjectRead])
@log_exceptions
def list_projects(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit)
    return list(db.scalars(stmt))


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
@log_exceptions
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = crud_project.create_project(db, project=payload)
    return project


@router.get("/{project_id}", response_model=ProjectRead)
@log_exceptions
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = crud_project.get_project(db, project_id=project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/update", response_model=ProjectRead)
@log_exceptions
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = crud_project.update_project(db, project_id=project_id, project=payload)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/{project_id}/delete")
@log_exceptions
def delete_project(project_id: str, db: Session = Depends(get_db)):
    success = crud_project.delete_project(db, project_id=project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
