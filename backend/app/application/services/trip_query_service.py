"""Trip 조회 서비스."""

from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository
from app.domain.value_objects.trip_id import TripId


class TripQueryService:
    """Trip 조회 서비스."""

    def __init__(self, trip_repository: TripRepository) -> None:
        """초기화."""
        self.trip_repository = trip_repository

    async def get_user_trips(self, user_id: str) -> list[Trip]:
        """사용자의 모든 Trip 조회."""
        return await self.trip_repository.find_by_user_id(user_id)

    async def get_trip_by_id(self, trip_id: str) -> Trip | None:
        """ID로 Trip 조회."""
        trip_id_obj = TripId.from_string(trip_id)
        return await self.trip_repository.find_by_id(trip_id_obj)