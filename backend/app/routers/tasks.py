import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _get_task_and_verify(task_id: str, db: Session, current_user: models.User) -> models.Task:
    """
    Helper: fetch a task and verify it belongs to the current user's project.
    Raises 404 or 403 as appropriate.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Data isolation: verify the task's project belongs to this user
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    if not project or project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return task


@router.post("", response_model=schemas.TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Create a task inside a project.
    Verifies the project exists and belongs to the current user.
    """
    # Check the target project belongs to the current user
    project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    task = models.Task(
        id=str(uuid.uuid4()),
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        project_id=payload.project_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=schemas.TaskOut)
def update_task(
    task_id: str,
    payload: schemas.TaskUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Update task fields. Supports partial updates (only provided fields change)."""
    task = _get_task_and_verify(task_id, db, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Delete a task."""
    task = _get_task_and_verify(task_id, db, current_user)
    db.delete(task)
    db.commit()
