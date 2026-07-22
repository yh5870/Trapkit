"""Trip 엔티티."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self
from uuid import UUID, uuid4

from app.domain.value_objects.trip_id import TripId


@dataclass(frozen=True)
class Trip:
    """Trip 도메인 엔티티."""

    id: TripId
    title: str
    destination: str
    purpose: list[str]
    user_id: str
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None
    cautions: list[dict] = field(default_factory=list)
    baggage_summary: list[dict] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        title: str,
        destination: str,
        purpose: list[str],
        user_id: str,
        duration_nights: int | None = None,
        departure_month: int | None = None,
        companions: str | None = None,
    ) -> Self:
        """새 Trip 생성."""
        return cls(
            id=TripId(uuid4()),
            title=title,
            destination=destination,
            purpose=purpose,
            user_id=user_id,
            duration_nights=duration_nights,
            departure_month=departure_month,
            companions=companions,
        )

    def update(
        self,
        title: str | None = None,
        destination: str | None = None,
        purpose: list[str] | None = None,
        duration_nights: int | None = None,
        departure_month: int | None = None,
        companions: str | None = None,
        cautions: list[dict] | None = None,
        baggage_summary: dict | None = None,
    ) -> Self:
        """Trip 업데이트."""
        return Trip(
            id=self.id,
            title=title if title is not None else self.title,
            destination=destination if destination is not None else self.destination,
            purpose=purpose if purpose is not None else self.purpose,
            user_id=self.user_id,
            duration_nights=duration_nights if duration_nights is not None else self.duration_nights,
            departure_month=departure_month if departure_month is not None else self.departure_month,
            companions=companions if companions is not None else self.companions,
            cautions=cautions if cautions is not None else self.cautions,
            baggage_summary=baggage_summary if baggage_summary is not None else self.baggage_summary,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )

    def add_caution(self, caution: dict) -> Self:
        """주의사항 추가."""
        new_cautions = self.cautions.copy()
        new_cautions.append(caution)
        return self.update(cautions=new_cautions)

    def update_baggage_summary(self, summary: list[dict]) -> Self:
        """수화물 요약 업데이트."""
        return self.update(baggage_summary=summary)