from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Secrets (loaded from .env — never commit) ──────────────
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    HF_TOKEN: str = ""

    # ── AI configuration ───────────────────────────────────────
    # Override in .env to switch models/providers without touching code
    HUGGINGFACE_API_URL: str = "https://router.huggingface.co/v1"
    HF_MODEL: str = "openai/gpt-oss-20b:novita"

    # ── App configuration ──────────────────────────────────────
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
