"""Trip 생성 Command.

Trip 생성 유스케이스를 위한 Command 패턴 구현.
CQRS 패턴의 Command 측면을 담당.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CreateTripCommand:
    """Trip 생성 Command."""

    user_id: str
    destination: str
    purpose: list[str]
    duration_nights: int | None = None
    departure_month: int | None = None
    companions: str | None = None