"""Trip 도메인 스키마.

A개발자가 정의한 Trip 도메인 모델에 맞는 Pydantic 스키마입니다.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class TripResponse(BaseModel):
    """Trip 응답 스키마."""

    id: str = Field(..., description="Trip ID")
    title: str = Field(..., min_length=1, max_length=255, description="여행 제목")
    destination: str = Field(..., min_length=1, max_length=255, description="여행지")
    purpose: list[str] = Field(default_factory=list, description="여행 목적")
    user_id: str = Field(..., description="사용자 ID")
    duration_nights: int | None = Field(None, ge=1, description="숙박일수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발월")
    companions: str | None = Field(None, max_length=255, description="동반자")
    cautions: list[dict[str, Any]] = Field(default_factory=list, description="주의사항")
    baggage_summary: list[dict[str, Any]] = Field(default_factory=list, description="수화물 요약")
    created_at: datetime = Field(..., description="생성일시")
    updated_at: datetime = Field(..., description="수정일시")

    # 진행률 (조회 시점 집계, DB에 저장하지 않음)
    items_count: int = Field(0, ge=0, description="전체 아이템 수")
    checked_count: int = Field(0, ge=0, description="체크 완료된 아이템 수")

    class Config:
        """Pydantic 설정."""

        from_attributes = True


class TripCreate(BaseModel):
    """Trip 생성 요청 스키마."""

    title: str = Field(..., min_length=1, max_length=255, description="여행 제목")
    destination: str = Field(..., min_length=1, max_length=255, description="여행지")
    purpose: list[str] = Field(..., min_length=1, description="여행 목적")
    duration_nights: int | None = Field(None, ge=1, description="숙박일수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발월")
    companions: str | None = Field(None, max_length=255, description="동반자")
    cautions: list[dict[str, Any]] = Field(default_factory=list, description="주의사항")
    baggage_summary: list[dict[str, Any]] = Field(default_factory=list, description="수화물 요약")


class TripUpdate(BaseModel):
    """Trip 수정 요청 스키마."""

    title: str | None = Field(None, min_length=1, max_length=255, description="여행 제목")
    destination: str | None = Field(None, min_length=1, max_length=255, description="여행지")
    purpose: list[str] | None = Field(None, min_length=1, description="여행 목적")
    duration_nights: int | None = Field(None, ge=1, description="숙박일수")
    departure_month: int | None = Field(None, ge=1, le=12, description="출발월")
    companions: str | None = Field(None, max_length=255, description="동반자")
    cautions: list[dict[str, Any]] | None = Field(None, description="주의사항")
    baggage_summary: list[dict[str, Any]] | None = Field(None, description="수화물 요약")


class TripListResponse(BaseModel):
    """Trip 목록 응답 스키마."""

    trips: list[TripResponse]
    total: int = Field(..., description="총 개수")
