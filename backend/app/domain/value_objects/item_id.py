"""ItemId 값 객체."""

from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True)
class ItemId:
    """Item 식별자 값 객체."""

    value: UUID