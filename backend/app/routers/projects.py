import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=List[schemas.ProjectSummary])
def list_projects(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    List all projects belonging to the current user.
    Includes task counters per status — used in the dashboard cards.
    Data isolation: filters by current_user.id so users never see each other's data.
    """
    projects = (
        db.query(models.Project)
        .filter(models.Project.user_id == current_user.id)
        .order_by(models.Project.created_at.desc())
        .all()
    )

    result = []
    for project in projects:
        tasks = project.tasks
        result.append(
            schemas.ProjectSummary(
                **{c.name: getattr(project, c.name) for c in project.__table__.columns},
                task_count=len(tasks),
                todo_count=sum(1 for t in tasks if t.status == models.TaskStatus.TODO),
                in_progress_count=sum(1 for t in tasks if t.status == models.TaskStatus.IN_PROGRESS),
                done_count=sum(1 for t in tasks if t.status == models.TaskStatus.DONE),
            )
        )
    return result


@router.post("", response_model=schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Create a new project for the current user."""
    project = models.Project(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        title=payload.title,
        description=payload.description,
        color=payload.color or "#6366f1",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}", response_model=schemas.ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Get a single project with all its tasks.
    Raises 404 if not found and 403 if it belongs to another user.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return project


@router.put("/{project_id}", response_model=schemas.ProjectOut)
def update_project(
    project_id: str,
    payload: schemas.ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update a project's title, description, or color."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Only update fields that were actually provided
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a project and all its tasks (cascade)."""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    db.delete(project)
    db.commit()
