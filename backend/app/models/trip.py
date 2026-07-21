"""Trip 모델."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .user import User


class Trip:
    """Trip 모델."""

    # TODO: 실제 SQLAlchemy Base 상속 모델로 변경
    # class Trip(Base):
    #     __tablename__ = "trips"
    #
    #     id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #     user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    #     user: Mapped["User"] = relationship(back_populates="trips")
    #     title: Mapped[str] = mapped_column(String(255))
    #     destination: Mapped[str] = mapped_column(String(255))
    #     purpose: Mapped[list[str]] = mapped_column(ARRAY(Text))
    #     duration_nights: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #     departure_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    #     companions: Mapped[str | None] = mapped_column(String(255), nullable=True)
    #     cautions: Mapped[dict] = mapped_column(JSON)
    #     baggage_summary: Mapped[dict] = mapped_column(JSON)
    #     created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    #     updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    #
    #     # relationships
    #     items: Mapped[list["ChecklistItem"]] = relationship(back_populates="trip", cascade="all, delete-orphan")
    #     memos: Mapped[list["Memo"]] = relationship(back_populates="trip", cascade="all, delete-orphan")

    pass


class ChecklistItem:
    """ChecklistItem 모델."""

    # TODO: 실제 SQLAlchemy Base 상속 모델로 변경
    # class ChecklistItem(Base):
    #     __tablename__ = "checklist_items"
    #
    #     id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #     trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.id"))
    #     trip: Mapped["Trip"] = relationship(back_populates="items")
    #     category: Mapped[str] = mapped_column(String(100))
    #     name: Mapped[str] = mapped_column(String(255))
    #     quantity: Mapped[str | None] = mapped_column(String(100), nullable=True)
    #     tip: Mapped[str | None] = mapped_column(Text, nullable=True)
    #     baggage_flag: Mapped[str | None] = mapped_column(String(50), nullable=True)
    #     source: Mapped[str] = mapped_column(String(20))  # 'ai' | 'user'
    #     checked: Mapped[bool] = mapped_column(default=False)
    #     sort_order: Mapped[int] = mapped_column(default=0)
    #     created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    #     updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    pass


class Memo:
    """Memo 모델."""

    # TODO: 실제 SQLAlchemy Base 상속 모델로 변경
    # class Memo(Base):
    #     __tablename__ = "memos"
    #
    #     id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #     trip_id: Mapped[UUID] = mapped_column(ForeignKey("trips.id"))
    #     trip: Mapped["Trip"] = relationship(back_populates="memos")
    #     content: Mapped[str] = mapped_column(Text, max_length=2000)
    #     created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    #     updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

    pass