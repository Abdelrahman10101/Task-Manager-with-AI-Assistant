from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Secrets (loaded from .env — never commit) ──────────────
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    HF_TOKEN: str = ""

    # ── Configuration (loaded from .config — safe to commit) ───
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    FRONTEND_URL: str = "http://localhost:5173"

    class Config:
        # Load secrets first, then config (later files override earlier ones)
        env_file = (".config", ".env")
        env_file_encoding = "utf-8"


settings = Settings()
