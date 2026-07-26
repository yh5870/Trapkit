"""ItemRepository 인터페이스."""

from abc import ABC, abstractmethod
from typing import Self

from app.domain.models.item import Item
from app.domain.value_objects.item_id import ItemId
from app.domain.value_objects.trip_id import TripId


class ItemRepository(ABC):
    """Item 저장소 인터페이스."""

    @abstractmethod
    async def save(self, item: Item) -> Item:
        """Item 저장."""
        pass

    @abstractmethod
    async def find_by_id(self, item_id: ItemId) -> Item | None:
        """ID로 Item 조회."""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (생성일 내림차순)."""
        pass

    @abstractmethod
    async def find_by_trip_id_sorted(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (sort_order 오름차순)."""
        pass

    @abstractmethod
    async def find_by_category(
        self,
        trip_id: TripId,
        category: str
    ) -> list[Item]:
        """Trip ID와 카테고리로 Item 조회."""
        pass

    @abstractmethod
    async def delete(self, item_id: ItemId) -> None:
        """Item 삭제."""
        pass

    @abstractmethod
    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Item 삭제 (Trip 삭제 시)."""
        pass

    @abstractmethod
    async def get_checked_count(self, trip_id: TripId) -> int:
        """Trip ID로 완료된 Item 수 조회."""
        pass

    @abstractmethod
    async def get_total_count(self, trip_id: TripId) -> int:
        """Trip ID로 전체 Item 수 조회."""
        pass

    @abstractmethod
    async def count_by_trip_ids(
        self,
        trip_ids: list[TripId],
    ) -> dict[str, tuple[int, int]]:
        """여러 Trip의 아이템 수를 한 번에 집계 (N+1 회피).

        목록 화면의 진행률 표시용. get_total_count/get_checked_count를
        여행마다 호출하면 쿼리가 2N번 발생하므로, GROUP BY로 1번에 처리한다.

        Args:
            trip_ids: 집계할 Trip ID 리스트

        Returns:
            {trip_id 문자열: (전체 수, 체크된 수)} 매핑.
            아이템이 하나도 없는 Trip은 키가 존재하지 않으므로
            호출측에서 (0, 0) 기본값 처리가 필요하다.
        """
        pass

    @abstractmethod
    async def update_sort_order(
        self,
        item_id: ItemId,
        new_order: int
    ) -> None:
        """Item 정렬 순서 업데이트."""
        pass