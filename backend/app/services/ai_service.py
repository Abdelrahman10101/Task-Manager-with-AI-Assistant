import httpx
import json
from app.config import settings
from app import models
from app.prompts.ai_prompts import (
    SUMMARIZE_SYSTEM,
    SUMMARIZE_USER,
    SUGGEST_SYSTEM,
    SUGGEST_USER,
)


def _hf_url() -> str:
    return f"{settings.HUGGINGFACE_API_URL}/chat/completions"


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {settings.HF_TOKEN}"}


def _format_tasks_for_prompt(tasks: list[models.Task]) -> str:
    """Format task list into a readable string for the AI prompt."""
    if not tasks:
        return "No tasks yet."

    lines = []
    for task in tasks:
        status_label = task.status.value.replace("_", " ").upper()
        priority_label = task.priority.value.upper()
        line = f"  [{status_label}] {task.title} (Priority: {priority_label})"
        if task.description:
            line += f"\n    Description: {task.description}"
        lines.append(line)
    return "\n".join(lines)


async def summarize_project(project: models.Project) -> str:
    """
    Call HuggingFace router (/v1/chat/completions) to summarize a project's tasks.

    Falls back to a local summary if HF_TOKEN is not set or the call fails.
    """
    tasks = project.tasks
    tasks_text = _format_tasks_for_prompt(tasks)

    todo = sum(1 for t in tasks if t.status == models.TaskStatus.TODO)
    in_progress = sum(1 for t in tasks if t.status == models.TaskStatus.IN_PROGRESS)
    done = sum(1 for t in tasks if t.status == models.TaskStatus.DONE)

    user_message = SUMMARIZE_USER.format(
        project_title=project.title,
        project_description=f"Description: {project.description}" if project.description else "",
        task_count=len(tasks),
        tasks_text=tasks_text,
        todo=todo,
        in_progress=in_progress,
        done=done,
    )

    if not settings.HF_TOKEN or settings.HF_TOKEN == "hf_your_token_here":
        return _local_fallback_summary(project.title, todo, in_progress, done, len(tasks))

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                _hf_url(),
                headers=_auth_headers(),
                json={
                    "model": settings.HF_MODEL,
                    "messages": [
                        {"role": "system", "content": SUMMARIZE_SYSTEM},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 400,
                    "temperature": 0.7,
                },
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    except httpx.HTTPError:
        return _local_fallback_summary(project.title, todo, in_progress, done, len(tasks))


def _local_fallback_summary(title: str, todo: int, in_progress: int, done: int, total: int) -> str:
    """Fallback summary computed locally when HF API is unavailable."""
    if total == 0:
        return f"**{title}** has no tasks yet. Start by adding tasks to track your progress."

    completion = round((done / total) * 100) if total > 0 else 0
    risk = "high" if in_progress == 0 and todo > 3 else "low"

    return (
        f"**{title}** is {completion}% complete with {total} total tasks. "
        f"Currently {in_progress} task(s) are in progress and {todo} remain to be started.\n\n"
        f"**Risk level:** {risk.upper()}\n\n"
        f"**Recommended next actions:**\n"
        f"1. Pick up one of the {todo} pending tasks and move it to In Progress\n"
        f"2. Review and close any blocked In Progress tasks\n"
        f"3. Ensure all tasks have clear descriptions and priorities set"
    )


async def suggest_tasks(title: str, description: str | None) -> list[dict]:
    """
    Call HuggingFace router to suggest an initial set of tasks for a new project.
    Returns a list of task dicts with title, description, and priority.
    """
    user_message = SUGGEST_USER.format(
        project_title=title,
        project_description=f"Project description: {description}" if description else "",
    )

    if not settings.HF_TOKEN or settings.HF_TOKEN == "hf_your_token_here":
        return _default_suggestions(title)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                _hf_url(),
                headers=_auth_headers(),
                json={
                    "model": settings.HF_MODEL,
                    "messages": [
                        {"role": "system", "content": SUGGEST_SYSTEM},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 600,
                    "temperature": 0.5,
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data["choices"][0]["message"]["content"].strip()

            # Parse JSON array from the response
            start = text.find("[")
            end = text.rfind("]") + 1
            if start != -1 and end > start:
                return json.loads(text[start:end])

    except Exception:
        pass

    return _default_suggestions(title)


def _default_suggestions(title: str) -> list[dict]:
    """Default task suggestions when AI is unavailable."""
    return [
        {"title": "Define project requirements", "description": f"Document the goals and scope of {title}.", "priority": "high"},
        {"title": "Set up project structure", "description": "Initialize repository and folder structure.", "priority": "high"},
        {"title": "Design system architecture", "description": "Plan the technical architecture and key components.", "priority": "medium"},
        {"title": "Implement core features", "description": "Build the main functionality of the project.", "priority": "medium"},
        {"title": "Write tests and documentation", "description": "Ensure code quality and document the project.", "priority": "low"},
    ]
