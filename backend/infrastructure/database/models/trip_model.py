"""Trip ORM Model."""

from datetime import datetime
from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import DateTime, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.config.database import Base

if TYPE_CHECKING:
    from infrastructure.database.models.item_model import ItemModel


class TripModel(Base):
    """Trip 테이블 ORM 모델."""

    __tablename__ = "trips"

    # Primary Key
    id: Mapped[UUID] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
    )

    # Foreign Keys
    user_id: Mapped[str] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )

    # Basic Fields
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)

    # JSON Fields
    purpose: Mapped[dict] = mapped_column(JSON, nullable=False)
    cautions: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)
    baggage_summary: Mapped[dict] = mapped_column(JSON, nullable=False, default=list)

    # Optional Fields
    duration_nights: Mapped[int | None] = mapped_column(nullable=True)
    departure_month: Mapped[int | None] = mapped_column(nullable=True)
    companions: Mapped[str | None] = mapped_column(String(255), nullable=True)

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
    items: Mapped[List["ItemModel"]] = relationship(
        "ItemModel", 
        back_populates="trip", 
        cascade="all, delete-orphan"
    )