"""Item 관련 Command."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Self


@dataclass(frozen=True)
class AddItemCommand:
    """Item 추가 Command."""

    trip_id: str
    category: str
    name: str
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    source: str = "user"  # "ai" | "user"


@dataclass(frozen=True)
class CheckItemCommand:
    """Item 체크/언체크 Command."""

    item_id: str
    checked: bool


@dataclass(frozen=True)
class UpdateItemCommand:
    """Item 수정 Command."""

    item_id: str
    name: str | None = None
    quantity: str | None = None
    tip: str | None = None
    baggage_flag: str | None = None
    checked: bool | None = None


@dataclass(frozen=True)
class DeleteItemCommand:
    """Item 삭제 Command."""

    item_id: str


@dataclass(frozen=True)
class UpdateSortOrderCommand:
    """Item 정렬 순서 변경 Command."""

    item_id: str
    new_order: int