from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.routers import auth, projects, tasks, ai

# Create all DB tables on startup (equivalent to running migrations for dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="REST API for managing projects and tasks with AI-powered summaries",
    version="1.0.0",
)

# ─── CORS ────────────────────────────────────────────────────────────────────
# Allow the Vite frontend (localhost:5173) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(ai.router)


@app.get("/", tags=["health"])
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Task Manager API is running"}
