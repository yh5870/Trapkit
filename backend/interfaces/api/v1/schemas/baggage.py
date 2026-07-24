"""수화물 체커 API 스키마."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


class BaggageCheckRequest(BaseModel):
    """수화물 판정 요청 스키마."""

    airline: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="항공사명 (예: '대한항공', '아시아나')"
    )
    product: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="제품명 (예: '맥북', '보조배터리', '우산')"
    )
    value: float | None = Field(
        None,
        ge=0,
        description="수량/크기 (선택사항)"
    )
    unit: str | None = Field(
        None,
        description="단위 (선택사항, inch, cm, kg, g, mg, oz, lb)"
    )

    model_config = ConfigDict(from_attributes=True)


class VerdictResponse(BaseModel):
    """판정 결과 응답 스키마."""

    verdict: str = Field(..., description="판정 타입 (allowed, conditional, forbidden)")
    label: str = Field(..., description="한국어 라벨")
    reason: str = Field(..., description="판정 이유")
    emoji: str = Field(..., description="이모지")
    color_code: str = Field(..., description="HTML 색상 코드")
    is_allowed: bool = Field(..., description="허용 여부")
    is_forbidden: bool = Field(..., description="불가 여부")

    @classmethod
    def from_domain(cls, verdict) -> "VerdictResponse":
        """도메인 Verdict에서 변환."""
        return cls(
            verdict=verdict.verdict.value,
            label=verdict.label,
            reason=verdict.reason,
            emoji=verdict.emoji,
            color_code=verdict.color_code,
            is_allowed=verdict.is_allowed,
            is_forbidden=verdict.is_forbidden,
        )


class BaggageCheckResponse(BaseModel):
    """수화물 판정 응답 스키마."""

    carry_on: VerdictResponse = Field(..., description="기내 반입 판정")
    checked: VerdictResponse = Field(..., description="위탁물로 판정")
    checked_at: datetime = Field(default_factory=datetime.utcnow, description="체크 시간")

    model_config = ConfigDict(from_attributes=True)