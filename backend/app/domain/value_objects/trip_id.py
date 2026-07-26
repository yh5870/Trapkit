"""TripId Value Object."""

from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class TripId:
    """Trip 식별자 Value Object."""

    value: UUID

    @classmethod
    def from_string(cls, value: str) -> "TripId":
        """문자열로부터 TripId 생성."""
        return cls(UUID(value))

    def __str__(self) -> str:
        """문자열로 변환."""
        return str(self.value)