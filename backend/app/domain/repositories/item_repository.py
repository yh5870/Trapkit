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
    async def update_sort_order(
        self,
        item_id: ItemId,
        new_order: int
    ) -> None:
        """Item 정렬 순서 업데이트."""
        pass