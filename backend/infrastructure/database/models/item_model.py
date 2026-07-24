"""Item ORM Model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, String, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.config.database import Base


class ItemModel(Base):
    """Item 테이블 ORM 모델.

    여행에 필요한 짐 항목을 나타냅니다.
    """

    __tablename__ = "items"

    # Primary Key
    id: Mapped[str] = mapped_column(
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

    # Basic Fields
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tip: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Baggage Flags
    # carry_on_only: 기내 반입만 가능
    # checked_only: 수화물로만 가능
    # restricted: 반입 제한
    # null: 제한 없음
    baggage_flag: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # Source: "ai" (AI 생성) 또는 "user" (사용자 직접 추가)
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
        index=True,
    )

    # Checked Status
    checked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    # Sort Order
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

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
    # trip = relationship("TripModel", back_populates="items")
