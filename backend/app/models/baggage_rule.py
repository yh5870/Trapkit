"""BaggageRule 모델."""

from datetime import datetime

from sqlalchemy import String, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column


class BaggageRule:
    """BaggageRule 모델."""

    # TODO: 실제 SQLAlchemy Base 상속 모델로 변경
    # class BaggageRule(Base):
    #     __tablename__ = "baggage_rules"
    #
    #     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #     item_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    #     display_name: Mapped[str] = mapped_column(String(255))
    #     aliases: Mapped[list[str]] = mapped_column(ARRAY(Text))
    #     unit: Mapped[str] = mapped_column(String(20))  # 'ml' | 'g' | 'mah_wh' | 'count' | 'none'
    #     carry_on_rule: Mapped[dict] = mapped_column(JSON)
    #     checked_rule: Mapped[dict] = mapped_column(JSON)
    #     tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    #     source: Mapped[str] = mapped_column(String(100))  # '국토교통부 고시', 'IATA'
    #     updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    #
    # class BaggageSearchLog(Base):
    #     __tablename__ = "baggage_search_logs"
    #
    #     id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #     user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    #     item: Mapped[str] = mapped_column(String(255))
    #     value: Mapped[float | None] = mapped_column(Integer, nullable=True)
    #     unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    #     flight_type: Mapped[str] = mapped_column(String(20))  # 'international' | 'domestic'
    #     result: Mapped[dict] = mapped_column(JSON)
    #     created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    pass