"""TripRepository 인터페이스."""

from abc import ABC, abstractmethod
from typing import Self

from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId


class TripRepository(ABC):
    """Trip 저장소 인터페이스."""

    @abstractmethod
    async def save(self, trip: Trip) -> Trip:
        """Trip 저장."""
        pass

    @abstractmethod
    async def find_by_id(self, trip_id: TripId) -> Trip | None:
        """ID로 Trip 조회."""
        pass

    @abstractmethod
    async def find_by_user_id(self, user_id: str) -> list[Trip]:
        """사용자 ID로 모든 Trip 조회."""
        pass

    @abstractmethod
    async def delete(self, trip_id: TripId) -> None:
        """Trip 삭제."""
        pass