"""Verdict 값 객체."""

from dataclasses import dataclass, field
from enum import Enum


class VerdictType(Enum):
    """판정 타입."""
    ALLOWED = "allowed"  # 허용
    CONDITIONAL = "conditional"  # 조건부 허용
    FORBIDDEN = "forbidden"  # 불가


@dataclass(frozen=True)
class Verdict:
    """수화물 규정 판정 결과."""

    verdict: VerdictType
    reason: str

    @property
    def label(self) -> str:
        """한국어 라벨."""
        if self.verdict == VerdictType.ALLOWED:
            return "가능 ○"
        elif self.verdict == VerdictType.CONDITIONAL:
            return "조건부 가능 △"
        else:  # FORBIDDEN
            return "불가 ✕"

    @property
    def emoji(self) -> str:
        """이모지."""
        if self.verdict == VerdictType.ALLOWED:
            return "✅"
        elif self.verdict == VerdictType.CONDITIONAL:
            return "⚠️"
        else:  # FORBIDDEN
            return "❌"

    @property
    def color_code(self) -> str:
        """HTML 색상 코드."""
        if self.verdict == VerdictType.ALLOWED:
            return "#10b981"  # green
        elif self.verdict == VerdictType.CONDITIONAL:
            return "#f59e0b"  # yellow
        else:  # FORBIDDEN
            return "#ef4444"  # red

    @property
    def is_allowed(self) -> bool:
        """허용 여부."""
        return self.verdict == VerdictType.ALLOWED

    @property
    def is_forbidden(self) -> bool:
        """불가 여부."""
        return self.verdict == VerdictType.FORBIDDEN

    def get_short_reason(self, max_length: int = 50) -> str:
        """짧은 이유 (최대 길이로 줄임)."""
        if len(self.reason) <= max_length:
            return self.reason
        return self.reason[:max_length - 3] + "..."