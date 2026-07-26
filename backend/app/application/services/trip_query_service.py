"""Trip 조회 서비스."""

from app.domain.models.trip import Trip
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.trip_repository import TripRepository
from app.domain.value_objects.trip_id import TripId


class TripQueryService:
    """Trip 조회 서비스."""

    def __init__(
        self,
        trip_repository: TripRepository,
        item_repository: ItemRepository | None = None,
    ) -> None:
        """초기화.

        Args:
            trip_repository: Trip 저장소
            item_repository: Item 저장소 (진행률 집계용, 선택).
                None이면 get_trip_progress가 빈 dict를 반환한다.
                기존 호출부와의 호환을 위해 선택 인자로 둔다.
        """
        self.trip_repository = trip_repository
        self.item_repository = item_repository

    async def get_user_trips(self, user_id: str) -> list[Trip]:
        """사용자의 모든 Trip 조회."""
        return await self.trip_repository.find_by_user_id(user_id)

    async def get_trip_by_id(self, trip_id: str) -> Trip | None:
        """ID로 Trip 조회."""
        trip_id_obj = TripId.from_string(trip_id)
        return await self.trip_repository.find_by_id(trip_id_obj)

    async def get_trip_progress(
        self,
        trips: list[Trip],
    ) -> dict[str, tuple[int, int]]:
        """Trip 목록의 진행률을 한 번에 집계.

        진행률(items_count/checked_count)은 DB에 저장하지 않고 조회 시점에
        계산한다. 저장 방식은 아이템 추가/삭제/체크마다 동기화가 필요해
        값이 실제와 어긋날 위험이 있기 때문이다.

        Args:
            trips: 집계 대상 Trip 리스트

        Returns:
            {trip_id 문자열: (전체 수, 체크된 수)} 매핑.
            아이템이 없는 Trip도 (0, 0)으로 채워 반환한다.
        """
        if self.item_repository is None or not trips:
            return {}

        counts = await self.item_repository.count_by_trip_ids(
            [trip.id for trip in trips]
        )

        # 아이템이 없는 Trip은 GROUP BY 결과에서 빠지므로 (0, 0)으로 보정
        return {
            str(trip.id.value): counts.get(str(trip.id.value), (0, 0))
            for trip in trips
        }
