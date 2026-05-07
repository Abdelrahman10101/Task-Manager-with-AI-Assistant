"""
AI system prompts for the HuggingFace router (OpenAI-compatible /v1/chat/completions).

Each prompt is split into:
  - SYSTEM: static role instruction (passed as role="system")
  - USER template: dynamic content (passed as role="user")

The caller interpolates project-specific variables into the USER template.
"""


# ── Summarize ─────────────────────────────────────────────────────────────────

SUMMARIZE_SYSTEM = (
    "You are a smart project management assistant. "
    "Analyze projects and provide concise, actionable summaries."
)

SUMMARIZE_USER = """\
Analyze this project and provide a concise summary.

Project: "{project_title}"
{project_description}

Tasks ({task_count} total):
{tasks_text}

Status breakdown: {todo} To Do, {in_progress} In Progress, {done} Done

Provide:
1. A 2-sentence overall project status assessment
2. Key risks or blockers (if any)
3. Top 3 recommended next actions

Be concise and actionable.\
"""


# ── Suggest tasks ─────────────────────────────────────────────────────────────

SUGGEST_SYSTEM = (
    "You are a project planning assistant. "
    "When asked, return ONLY a valid JSON array — no extra text, no markdown fences."
)

SUGGEST_USER = """\
Suggest 5 concrete tasks for this project.

Project title: "{project_title}"
{project_description}

Return ONLY a valid JSON array with exactly 5 objects. Each object must have:
- "title": short task name (max 8 words)
- "description": one sentence explaining the task
- "priority": one of "low", "medium", "high"

Example format:
[
  {{"title": "Set up project repository", "description": "Initialize git repo and configure CI/CD pipeline.", "priority": "high"}},
  ...
]

Return only the JSON array, no other text.\
"""
