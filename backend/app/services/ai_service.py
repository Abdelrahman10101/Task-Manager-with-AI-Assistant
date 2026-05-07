import httpx
import json
from app.config import settings
from app import models


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
    Call HuggingFace Inference API to summarize a project's tasks.
    Uses Mistral-7B-Instruct for instruction-following quality.

    Falls back to a local summary if HF_TOKEN is not set.
    """
    tasks = project.tasks
    tasks_text = _format_tasks_for_prompt(tasks)

    todo = sum(1 for t in tasks if t.status == models.TaskStatus.TODO)
    in_progress = sum(1 for t in tasks if t.status == models.TaskStatus.IN_PROGRESS)
    done = sum(1 for t in tasks if t.status == models.TaskStatus.DONE)

    prompt = f"""<s>[INST] You are a smart project management assistant. Analyze this project and provide a concise summary.

Project: "{project.title}"
{f'Description: {project.description}' if project.description else ''}

Tasks ({len(tasks)} total):
{tasks_text}

Status breakdown: {todo} To Do, {in_progress} In Progress, {done} Done

Provide:
1. A 2-sentence overall project status assessment
2. Key risks or blockers (if any)
3. Top 3 recommended next actions

Be concise and actionable. [/INST]"""

    # If no HF token, return a local computed summary
    if not settings.HF_TOKEN or settings.HF_TOKEN == "hf_your_token_here":
        return _local_fallback_summary(project.title, todo, in_progress, done, len(tasks))

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 400,
                        "temperature": 0.7,
                        "return_full_text": False,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and data:
                return data[0].get("generated_text", "").strip()
            return "Could not generate summary. Please try again."

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
    Call HuggingFace to suggest an initial set of tasks for a new project.
    Returns a list of task dicts with title, description, and priority.
    """
    prompt = f"""<s>[INST] You are a project planning assistant. Suggest 5 concrete tasks for this project.

Project title: "{title}"
{f'Project description: {description}' if description else ''}

Return ONLY a valid JSON array with exactly 5 objects. Each object must have:
- "title": short task name (max 8 words)
- "description": one sentence explaining the task
- "priority": one of "low", "medium", "high"

Example format:
[
  {{"title": "Set up project repository", "description": "Initialize git repo and configure CI/CD pipeline.", "priority": "high"}},
  ...
]

Return only the JSON array, no other text. [/INST]"""

    if not settings.HF_TOKEN or settings.HF_TOKEN == "hf_your_token_here":
        return _default_suggestions(title)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                headers={"Authorization": f"Bearer {settings.HF_TOKEN}"},
                json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 600, "temperature": 0.5, "return_full_text": False},
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data[0].get("generated_text", "") if isinstance(data, list) else ""

            # Parse JSON from the response
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
