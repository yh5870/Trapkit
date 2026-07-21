"""AI 응답 스키마."""

from typing import Any

from pydantic import BaseModel


class AICategory(BaseModel):
    """AI 카테고리."""

    name: str
    items: list[dict[str, Any]]


class AICautions(BaseModel):
    """AI 주의사항."""

    category: str
    text: str
    confidence: str  # 'stable' | 'check_required'


class AITripResponse(BaseModel):
    """AI 트립 응답."""

    trip_title: str
    categories: list[AICategory]
    cautions: list[AICautions]
    baggage_summary: list[dict[str, Any]]