"""MemoId 값 객체."""

from uuid import UUID
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoId:
    """메모 식별자 값 객체."""

    value: UUID