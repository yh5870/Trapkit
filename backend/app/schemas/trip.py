"""트립 스키마."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChecklistItem(BaseModel):
    """체크리스트 항목."""

    id: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None  # 'carry_on_only' | 'checked_only' | 'restricted'
    source: str  # 'ai' | 'user'
    checked: bool = False


class Category(BaseModel):
    """카테고리."""

    name: str
    items: list[ChecklistItem]


class Cautions(BaseModel):
    """주의사항."""

    category: str
    text: str
    confidence: str  # 'stable' | 'check_required'


class Memo(BaseModel):
    """메모."""

    id: str
    content: str
    updated_at: str


class GenerateTripRequest(BaseModel):
    """AI 리스트 생성 요청."""

    destination: str = Field(..., min_length=1, max_length=255)
    purpose: list[str] = Field(default_factory=list)
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None


class GenerateTripResponse(BaseModel):
    """AI 리스트 생성 응답."""

    trip_title: str
    categories: list[Category]
    cautions: list[Cautions]
    baggage_summary: list[dict[str, Any]]
    trip_id: str | None = None  # 로그인 시 DB 저장됨


class TripSummary(BaseModel):
    """여행 요약."""

    id: str
    title: str
    meta: str
    progress: dict[str, int]  # {'checked': 8, 'total': 26}
    status: Literal["ongoing", "done"]


class TripListResponse(BaseModel):
    """여행 목록 응답."""

    trips: list[TripSummary]


class TripDetailResponse(BaseModel):
    """여행 상세 응답."""

    trip_title: str
    meta: str
    progress: dict[str, int]
    categories: list[Category]
    cautions: list[Cautions]
    baggage_summary: list[dict[str, Any]]
    memos: list[Memo]


class UpdateTripRequest(BaseModel):
    """여행 수정 요청."""

    title: str | None = None


class AddItemRequest(BaseModel):
    """항목 추가 요청."""

    category: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)


class UpdateItemRequest(BaseModel):
    """항목 수정 요청."""

    name: str | None = None
    quantity: str | None = None
    tip: str | None = None
    checked: bool | None = None


class AddMemoRequest(BaseModel):
    """메모 추가 요청."""

    content: str = Field(..., min_length=1, max_length=2000)


class UpdateMemoRequest(BaseModel):
    """메모 수정 요청."""

    content: str = Field(..., min_length=1, max_length=2000)