"""설정 (환경변수, DB 연결)."""

from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 프로젝트 루트 (backend/). config.py = backend/app/config.py 기준으로 2단계 상위.
# 상대경로 ".env"는 실행 CWD 기준으로 풀리기 때문에, backend 밖에서 uvicorn을
# 띄우면 .env를 못 찾아 DATABASE_URL/JWT_SECRET missing 으로 죽는다.
# (app 패키지가 editable 설치되어 있어 import 자체는 어디서든 성공하므로
#  이 오류가 '설정 누락'처럼 보여 원인 파악이 어려웠음)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """앱 설정."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
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

    # AI (선택사항 - 없으면 임시 응답 반환)
    GEMINI_API_KEY: str | None = Field(None, description="Google Gemini API 키")
    GEMINI_MODEL: str = "gemini-1.5-flash"
    GLM_API_KEY: str | None = Field(None, description="智谱AI GLM API 키")
    GLM_MODEL: str = "glm-4"
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

    @field_validator(
        "DATABASE_URL",
        "JWT_SECRET",
        "GLM_API_KEY",
        "GEMINI_API_KEY",
        "REDIS_URL",
        "GLM_MODEL",
        "GEMINI_MODEL",
        "ENVIRONMENT",
        mode="before",
    )
    @classmethod
    def strip_whitespace(cls, v: Any) -> Any:
        """문자열 설정값의 앞뒤 공백/개행 제거.

        대시보드(Render 등)에 값을 붙여넣을 때 끝에 개행이 섞여 들어가는 일이
        잦다. 예를 들어 DATABASE_URL 끝에 '\\n' 이 붙으면 DB 이름이
        'postgres\\n' 으로 해석되어 InvalidCatalogNameError 가 발생하고,
        JWT_SECRET 에 붙으면 토큰 검증이 조용히 실패해 원인 파악이 어렵다.

        Args:
            v: 원본 설정값

        Returns:
            문자열이면 strip() 결과, 아니면 원본 그대로
        """
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """CORS 오리진 파싱."""
        if isinstance(v, str):
            # 빈 항목 제거 (예: 끝에 콤마가 붙은 경우)
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """설정 캐시 반환."""
    return Settings()


settings: Settings = get_settings()