from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str    = "vitor-balbino-martins"
    PROJECT_VERSION: str = "0.1.0"
    ENV: str             = "development"
    DEBUG: bool          = False
    API_V1_PREFIX: str   = "/api/v1"

    # Security
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ACCESS_TOKEN_EXPIRE_MINUTES: int  = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080

    # Logging
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost:5432/dbname"
    CORS_ORIGINS: list[str] = ["*"]
    RAG_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_DEVICE: str = "cuda"
    RAG_COLLECTION_NAME: str = "customer_support_tickets"
    RAG_TOP_K: int = 5
    RAG_ASSETS_DIR: str = "assets"
    RAG_SYNC_DATABASE_URL: str | None = None
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT_SECONDS: int = 600
    AI_TRACE_LOG: str = "logs/ai_traces.jsonl"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
