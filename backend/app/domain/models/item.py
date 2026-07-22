"""Item 엔티티."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Self

from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from app.domain.value_objects.item_id import ItemId
from app.domain.value_objects.memo_id import MemoId


@dataclass(frozen=True)
class Item:
    """여행에 필요한 짐 항목 엔티티."""

    id: ItemId
    trip_id: TripId
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    source: str = "user"  # "ai" | "user"
    checked: bool = False
    sort_order: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        trip_id: TripId,
        category: str,
        name: str,
        quantity: str | None = None,
        tip: str | None = None,
    ) -> Self:
        """새 Item 생성."""
        return cls(
            id=ItemId(UUID()),
            trip_id=trip_id,
            category=category,
            name=name,
            quantity=quantity,
            tip=tip,
            baggage_flag=None,  # 기본값: null
            source="user",    # 기본값: user
            checked=False,    # 기본값: False
            sort_order=0,      # 기본값: 0
        )

    def update(
        self,
        name: str | None = None,
        quantity: str | None = None,
        tip: str | None = None,
        baggage_flag: str | None = None,
        checked: bool | None = None,
    ) -> Self:
        """Item 업데이트."""
        return Item(
            id=self.id,
            trip_id=self.trip_id,
            category=self.category,
            name=name if name is not None else self.name,
            quantity=quantity if quantity is not None else self.quantity,
            tip=tip if tip is not None else self.tip,
            baggage_flag=baggage_flag if baggage_flag is not None else self.baggage_flag,
            source=self.source,
            checked=checked if checked is not None else self.checked,
            created_at=self.created_at,
            updated_at=datetime.utcnow() if (
                name is not None or
                quantity is not None or
                baggage_flag is not None or
                checked is not None
            ) else self.updated_at,
        )

    def check(self) -> Self:
        """체크박스 항목 완료 처리."""
        return self.update(checked=True)

    def uncheck(self) -> Self:
        """체크박스 항목 완료 취소."""
        return self.update(checked=False)

    def sort_order_up(self, new_order: int) -> Self:
        """정렬 순서 변경."""
        return self.update(sort_order=new_order)

    def update_source(self) -> Self:
        """소스를 AI로 변경."""
        return self.update(source="ai")

    def update_baggage_flag(self, flag: str) -> Self:
        """수화물 규정 플래그 변경."""
        return self.update(baggage_flag=flag)


@dataclass(frozen=True)
class ItemList:
    """항목 목록 (전체)."""

    items: list[Item] = field(default_factory=list)

    def total_items(self) -> int:
        """전체 항목 수."""
        return len(self.items)

    def checked_items(self) -> int:
        """완료된 항목 수."""
        return sum(1 for item in self.items if item.checked)

    def completion_rate(self) -> float:
        """완료율."""
        total = self.total_items()
        checked = self.checked_items()
        return checked / total * 100 if total > 0 else 0.0

    def pending_items(self) -> list[Item]:
        """미완료 항목 리스트."""
        return [item for item in self.items if not item.checked]

    def checked_items_by_category(self) -> dict[str, list[Item]]:
        """카테고리별 완료 항목 그룹화."""
        grouped = {}
        for item in self.items:
            if item.checked:
                category = item.category
                if category not in grouped:
                    grouped[category] = []
                grouped[category].append(item)
        return grouped


@dataclass(frozen=True)
class Memo:
    """메모 엔티티."""

    id: MemoId
    trip_id: TripId
    content: str  # 최대 2,000자 (Text 타입)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(
        cls,
        trip_id: TripId,
        content: str,
    ) -> Self:
        """새 Memo 생성."""
        # 길이 검증
        if len(content) > 2000:
            raise ValueError("메모는 최대 2,000자까지 작성할 수 있습니다.")

        return cls(
            id=MemoId(UUID()),
            trip_id=trip_id,
            content=content,
        )

    def update_content(self, content: str) -> Self:
        """메모 내용 업데이트."""
        if len(content) > 2000:
            raise ValueError("메모는 최대 2,000자까지 작성할 수 있습니다.")
        return self.update(content=content)
```