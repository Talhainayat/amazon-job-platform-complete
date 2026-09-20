"""
Application configuration.

All sensitive/environment-specific values come from environment variables
(loaded from a `.env` file in local development via python-dotenv).
Never hard-code secrets here.
"""
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict  # pyright: ignore[reportMissingImports]

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "Job Platform API"
    APP_VERSION: str = "1.1.0"
    ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./job_platform.db"

    SECRET_KEY: str = "CHANGE_ME_INSECURE_DEV_ONLY_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    AI_API_KEY: str = ""
    AI_PROVIDER: str = "none"

    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@example.com"

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""
    TWILIO_SMS_NUMBER: str = ""
    ADMIN_ALERT_PHONE_NUMBER: str = ""
    ALERT_WEBHOOK_URL: str = ""
    HIGH_MATCH_THRESHOLD: float = 80.0

    JOB_FEED_URL: str = ""
    JOB_FEED_SOURCE: str = "sample_feed"
    JOB_MONITOR_ENABLED: bool = True
    JOB_MONITOR_INTERVAL_SECONDS: int = 60
    LOG_LEVEL: str = "INFO"
    LIVE_JOB_FEED_URL: str = "https://arbeitnow.com/api/job-board-api"
    FRANKFURTER_URL: str = "https://api.frankfurter.app/latest"
    IP_GEOLOCATION_URL: str = "http://ip-api.com/json/"

    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    MATCH_WEIGHT_LOCATION: int = 35
    MATCH_WEIGHT_SKILLS: int = 20
    MATCH_WEIGHT_JOB_TYPE: int = 15
    MATCH_WEIGHT_SHIFT: int = 15
    MATCH_WEIGHT_EXPERIENCE: int = 8
    MATCH_WEIGHT_PAY: int = 7

    UPLOAD_DIR: str = str(BACKEND_DIR / "uploads")
    MAX_RESUME_BYTES: int = 5 * 1024 * 1024

    SEED_DEMO_DATA: bool = True

    @model_validator(mode="after")
    def validate_runtime_settings(self):
        if self.ENV.lower() == "production":
            if self.DEBUG:
                raise ValueError("DEBUG must be false in production")
            if not self.SECRET_KEY or self.SECRET_KEY.startswith("CHANGE_ME"):
                raise ValueError("SECRET_KEY must be set to a strong value in production")
            if not self.CORS_ORIGINS or "*" in self.CORS_ORIGINS:
                raise ValueError("CORS_ORIGINS must contain explicit production origins")
            if self.SEED_DEMO_DATA:
                raise ValueError("SEED_DEMO_DATA must be false in production")
        return self

    model_config = SettingsConfigDict(
        env_file=(str(BACKEND_DIR.parent / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
