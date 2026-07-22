"""Memo ORM Model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.config.database import Base


class MemoModel(Base):
    """Memo 테이블 ORM 모델.

    여행에 관한 메모/기록을 저장합니다.
    """

    __tablename__ = "memos"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
    )

    # Foreign Key
    trip_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    # Content (최대 2,000자)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # trip = relationship("TripModel", back_populates="memos")
