"""ItemId 값 객체."""

from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True)
class ItemId:
    """Item 식별자 값 객체."""

    value: UUID

    @classmethod
    def from_string(cls, item_id: str) -> "ItemId":
        """문자열에서 ItemId 생성."""
        return cls(value=UUID(item_id))