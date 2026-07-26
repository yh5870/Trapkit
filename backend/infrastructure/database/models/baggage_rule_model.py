"""BaggageRule ORM Model."""

from sqlalchemy import Column, Integer, String, DateTime, func, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column
from shared.config.database import Base


class BaggageRuleModel(Base):
    """수화물 규정 데이터베이스 모델."""

    __tablename__ = "baggage_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    aliases: Mapped[dict] = mapped_column(JSON, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    carry_on_rule: Mapped[dict] = mapped_column(JSON, nullable=False)
    checked_rule: Mapped[dict] = mapped_column(JSON, nullable=False)
    tips: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, server_default="iata")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def to_dict(self) -> dict:
        """데이터베이스 모델을 딕셔너리로 변환.

        Returns:
            {
                "item_key": str,
                "display_name": str,
                "aliases": list[str],
                "unit": str,
                "carry_on_rule": dict,
                "checked_rule": dict,
                "tips": str | None,
                "source": str
            }
        """
        return {
            "item_key": self.item_key,
            "display_name": self.display_name,
            "aliases": self.aliases,
            "unit": self.unit,
            "carry_on_rule": self.carry_on_rule,
            "checked_rule": self.checked_rule,
            "tips": self.tips,
            "source": self.source,
        }

    def __repr__(self) -> str:
        return (
            f"<BaggageRuleModel(id={self.id}, item_key='{self.item_key}', "
            f"display_name='{self.display_name}')>"
        )