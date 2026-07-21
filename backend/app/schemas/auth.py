"""인증 스키마."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """회원가입 요청."""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    nickname: str = Field(..., min_length=1, max_length=50)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """비밀번호 규칙 검증 (영문+숫자 조합)."""
        if not any(c.isalpha() for c in v):
            raise ValueError("비밀번호는 영문을 포함해야 합니다.")
        if not any(c.isdigit() for c in v):
            raise ValueError("비밀번호는 숫자를 포함해야 합니다.")
        return v


class LoginRequest(BaseModel):
    """로그인 요청."""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserResponse(BaseModel):
    """사용자 응답."""

    id: str
    email: str
    nickname: str
    created_at: str


class TokenResponse(BaseModel):
    """토큰 응답."""

    access_token: str
    token_type: str = "Bearer"
    user: UserResponse