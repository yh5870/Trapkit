"""MemoRepository 인터페이스."""

from abc import ABC, abstractmethod
from typing import Self

from app.domain.models.item import Memo
from app.domain.value_objects.memo_id import MemoId
from app.domain.value_objects.trip_id import TripId


class MemoRepository(ABC):
    """Memo 저장소 인터페이스."""

    @abstractmethod
    async def save(self, memo: Memo) -> Memo:
        """Memo 저장."""
        pass

    @abstractmethod
    async def find_by_id(self, memo_id: MemoId) -> Memo | None:
        """ID로 Memo 조회."""
        pass

    @abstractmethod
    async def find_by_trip_id(self, trip_id: TripId) -> list[Memo]:
        """Trip ID로 모든 Memo 조회 (생성일 내림차순)."""
        pass

    @abstractmethod
    async def delete(self, memo_id: MemoId) -> None:
        """Memo 삭제."""
        pass

    @abstractmethod
    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Memo 삭제 (Trip 삭제 시)."""
        pass

    @abstractmethod
    async def get_count(self, trip_id: TripId) -> int:
        """Trip ID로 Memo 수 조회."""
        pass