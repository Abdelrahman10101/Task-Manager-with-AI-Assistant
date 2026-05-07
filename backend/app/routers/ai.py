from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.auth import get_current_user
from app.services.ai_service import summarize_project, suggest_tasks

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/summarize", response_model=schemas.AISummarizeResponse)
async def ai_summarize(
    payload: schemas.AISummarizeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Generate an AI summary of a project's tasks.
    Calls HuggingFace Mistral-7B to analyze task statuses and suggest next actions.
    """
    project = db.query(models.Project).filter(models.Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    summary = await summarize_project(project)
    return {"summary": summary}


@router.post("/suggest", response_model=schemas.AISuggestResponse)
async def ai_suggest(
    payload: schemas.AISuggestRequest,
    current_user: models.User = Depends(get_current_user),
):
    """
    Suggest an initial set of tasks for a new project based on its title/description.
    Returns 5 task suggestions with title, description, and priority.
    """
    suggestions = await suggest_tasks(payload.project_title, payload.project_description)
    return {"suggestions": suggestions}
