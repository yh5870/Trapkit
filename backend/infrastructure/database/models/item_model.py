"""Item ORM Model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.config.database import Base

if TYPE_CHECKING:
    from infrastructure.database.models.trip_model import TripModel


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
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic Fields
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tip: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Baggage Flags
    baggage_flag: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True,
    )

    # Source
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

    # 🟢 순환 참조를 방지하도록 relationship 작성
    trip: Mapped["TripModel"] = relationship("TripModel", back_populates="items")