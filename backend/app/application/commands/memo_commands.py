"""Memo 관련 Command."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AddMemoCommand:
    """Memo 추가 Command."""

    trip_id: str
    content: str  # 최대 2,000자


@dataclass(frozen=True)
class UpdateMemoCommand:
    """Memo 수정 Command."""

    memo_id: str
    content: str  # 최대 2,000자


@dataclass(frozen=True)
class DeleteMemoCommand:
    """Memo 삭제 Command."""

    memo_id: str