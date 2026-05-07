from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.models import TaskStatus, Priority


# ─── User Schemas ────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ─── Task Schemas ─────────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    due_date: Optional[datetime] = None
    project_id: str


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None


class TaskOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: Priority
    due_date: Optional[datetime]
    project_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Project Schemas ──────────────────────────────────────────────────────────

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    color: Optional[str] = "#6366f1"


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


class ProjectOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    color: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    tasks: List[TaskOut] = []

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    """Project without tasks — used in list views"""
    id: str
    title: str
    description: Optional[str]
    color: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    task_count: int = 0
    todo_count: int = 0
    in_progress_count: int = 0
    done_count: int = 0

    class Config:
        from_attributes = True


# ─── AI Schemas ───────────────────────────────────────────────────────────────

class AISummarizeRequest(BaseModel):
    project_id: str


class AISummarizeResponse(BaseModel):
    summary: str


class AISuggestRequest(BaseModel):
    project_title: str
    project_description: Optional[str] = None


class AISuggestResponse(BaseModel):
    suggestions: List[dict]
