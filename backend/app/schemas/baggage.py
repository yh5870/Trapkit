"""수화물 체커 스키마."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class BaggageCheckRequest(BaseModel):
    """수화물 판정 요청."""

    item: str = Field(..., min_length=1, max_length=255)
    value: float | None = None
    unit: str = Field(default="ml")  # 'ml' | 'g' | 'mAh' | 'Wh' | 'cm' | '개'
    flight_type: Literal["international", "domestic"] = "international"


class Verdict(BaseModel):
    """판정."""

    verdict: Literal["allowed", "conditional", "forbidden"]
    label: str
    reason: str


class BaggageCheckResponse(BaseModel):
    """수화물 판정 응답."""

    item: str
    normalized_key: str
    converted: str | None = None
    carry_on: Verdict
    checked: Verdict
    tips: str | None = None
    source: str  # 'rule_db' | 'ai'
    reference: str