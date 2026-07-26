"""Trip API schemas.

API 요청 및 응답 데이터 구조를 정의합니다.
Pydantic으로 자동 검증 및 직렬화됩니다.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TripResponse(BaseModel):
    """트립 응답 스키마."""

    id: str = Field(..., description="트립 ID (UUID)")
    user_id: str = Field(..., description="사용자 ID")
    title: str = Field(..., min_length=1, max_length=200, description="트립 제목")
    destination: str = Field(..., min_length=1, max_length=100, description="여행지")
    purpose: list[str] = Field(default_factory=list, description="여행 목적")
    duration_nights: int | None = Field(None, ge=1, description="박수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발 월")
    companions: str | None = Field(None, max_length=100, description="동행인")
    cautions: list[dict[str, Any]] = Field(
        default_factory=list,
        description="주의사항 목록"
    )
    baggage_summary: list[dict[str, Any]] = Field(
        default_factory=list,
        description="수하물 요약"
    )
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    class Config:
        """Pydantic 설정."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user-123",
                "title": "도쿄 여행",
                "destination": "일본 도쿄",
                "purpose": ["쇼핑", "음식 탐방"],
                "duration_nights": 5,
                "departure_month": 8,
                "companions": "가족 3인",
                "cautions": [],
                "baggage_summary": [],
                "created_at": "2026-07-21T12:00:00Z",
                "updated_at": "2026-07-21T12:00:00Z",
            }
        }


class TripCreateRequest(BaseModel):
    """트립 생성 요청 스키마."""

    title: str = Field(..., min_length=1, max_length=200, description="트립 제목")
    destination: str = Field(..., min_length=1, max_length=100, description="여행지")
    purpose: list[str] = Field(
        default_factory=list,
        min_length=1,
        description="여행 목적 (최소 1개)"
    )
    duration_nights: int | None = Field(None, ge=1, description="박수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발 월")
    companions: str | None = Field(None, max_length=100, description="동행인")

    class Config:
        """Pydantic 설정."""

        json_schema_extra = {
            "example": {
                "title": "도쿄 여행",
                "destination": "일본 도쿄",
                "purpose": ["쇼핑", "음식 탐방"],
                "duration_nights": 5,
                "departure_month": 8,
                "companions": "가족 3인",
            }
        }


class TripUpdateRequest(BaseModel):
    """트립 수정 요청 스키마."""

    title: str | None = Field(None, min_length=1, max_length=200, description="트립 제목")
    destination: str | None = Field(None, min_length=1, max_length=100, description="여행지")
    purpose: list[str] | None = Field(None, min_length=1, description="여행 목적")
    duration_nights: int | None = Field(None, ge=1, description="박수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발 월")
    companions: str | None = Field(None, max_length=100, description="동행인")

    class Config:
        """Pydantic 설정."""

        json_schema_extra = {
            "example": {
                "title": "도쿄 여행",
                "duration_nights": 7,
            }
        }


class TripDeleteResponse(BaseModel):
    """트립 삭제 응답 스키마."""

    id: str = Field(..., description="삭제된 트립 ID")
    message: str = Field(..., description="삭제 메시지")

    class Config:
        """Pydantic 설정."""

        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "message": "트립이 삭제되었습니다.",
            }
        }