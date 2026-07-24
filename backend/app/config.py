"""설정 (환경변수, DB 연결)."""

from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱 설정."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL 연결 URL")

    # JWT
    JWT_SECRET: str = Field(..., min_length=32, description="JWT 시크릿 키")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7일

    # AI
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API 키")
    GEMINI_MODEL: str = Field(default="gemini-3.5-flash", description="Gemini 모델")
    AI_MAX_TOKENS: int = 2000
    AI_CACHE_TTL: int = 86400  # 24시간

    # Redis
    REDIS_URL: str | None = Field(None, description="Redis 연결 URL")

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000"  # 프론트엔드 포트
    ]

    # Environment
    ENVIRONMENT: str = "development"

    # Rate Limiting (requests per minute)
    RATE_LIMIT_ANONYMOUS: int = 5
    RATE_LIMIT_AUTHENTICATED: int = 20

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """CORS 오리진 파싱."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """설정 캐시 반환."""
    return Settings()


settings: Settings = get_settings()