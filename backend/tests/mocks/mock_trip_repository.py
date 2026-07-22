"""Mock TripRepository for testing.

인메모리 저장소로 B개발자가 DB 구현을 완료하기 전까지
도메인 로직 테스트를 진행할 수 있습니다.
"""

from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository
from app.domain.value_objects.trip_id import TripId


class MockTripRepository(TripRepository):
    """인메모리 Mock Trip 저장소."""

    def __init__(self) -> None:
        """초기화."""
        self._trips: dict[str, Trip] = {}

    async def save(self, trip: Trip) -> Trip:
        """Trip 저장."""
        trip_id_str = str(trip.id.value)
        self._trips[trip_id_str] = trip
        return trip

    async def find_by_id(self, trip_id: TripId) -> Trip | None:
        """ID로 Trip 조회."""
        trip_id_str = str(trip_id.value)
        return self._trips.get(trip_id_str)

    async def find_by_user_id(self, user_id: str) -> list[Trip]:
        """사용자 ID로 모든 Trip 조회."""
        return [trip for trip in self._trips.values() if trip.user_id == user_id]

    async def delete(self, trip_id: TripId) -> None:
        """Trip 삭제."""
        trip_id_str = str(trip_id.value)
        self._trips.pop(trip_id_str, None)

    def clear(self) -> None:
        """모든 데이터 삭제 (테스트용)."""
        self._trips.clear()