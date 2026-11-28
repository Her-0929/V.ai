from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str = "HER AI"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Local LLM - Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:1.7b"
    OLLAMA_TIMEOUT_SECONDS: int = 120

    # RAG configuration
    RAG_TOP_K: int = 5

    # Cloud LLM Providers (optional — leave blank for local-only mode)
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_MODEL: str = "meta-llama/llama-3.1-8b-instruct:free"
    # Active provider: "ollama" | "groq" | "gemini" | "openrouter"
    LLM_PROVIDER: str = "ollama"
    LLM_ENABLE_FALLBACK: bool = True

    # Security & JWT Configuration
    JWT_SECRET_KEY: str = "her-ai-secret-key-change-in-production-1234567890abcdef"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # Rate Limiting (slowapi string formats, e.g. "30/minute")
    RATE_LIMIT_CHAT: str = "30/minute"
    RATE_LIMIT_SEARCH: str = "60/minute"
    RATE_LIMIT_INGEST: str = "20/minute"
    RATE_LIMIT_DEFAULT: str = "120/minute"

    # Environment-specific CORS restrictions (comma-separated origins)
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173,https://v-ai-nine.vercel.app"

    # Artifact Storage & Upload Limits (Milestone 12)
    ARTIFACT_STORAGE_DIR: str = "storage/artifacts"
    ARTIFACT_MAX_FILE_SIZE_BYTES: int = 26_214_400  # 25 MiB

    @property
    def allowed_cors_origins(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Always guarantee deployed Vercel frontend domains are permitted
        guaranteed = ["https://v-ai-nine.vercel.app"]
        for g in guaranteed:
            if g not in origins:
                origins.append(g)
        return origins


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
