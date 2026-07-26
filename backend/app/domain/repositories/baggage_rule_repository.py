"""BaggageRuleRepository 인터페이스."""

from abc import ABC, abstractmethod
from typing import Self

from app.domain.value_objects.verdict import Verdict
from shared.utils.normalizer import normalize_airline, normalize_product


class BaggageRuleRepository(ABC):
    """수화물 규정 저장소 인터페이스."""

    @abstractmethod
    async def find_by_key(self, item_key: str) -> dict | None:
        """키로 규칙 조회.

        Returns:
            {
                "item_key": str,
                "display_name": str,
                "aliases": list[str],
                "unit": str,
                "carry_on_rule": dict,
                "checked_rule": dict,
                "tips": str | None
            } | None
        """
        pass

    @abstractmethod
    async def find_by_normalized_key(self, normalized_key: str) -> dict | None:
        """정규화된 키로 규칙 조회.

        Returns:
            {
                "item_key": str,
                "display_name": str,
                "aliases": list[str],
                "unit": str,
                "carry_on_rule": dict,
                "checked_rule": dict,
                "tips": str | None
            } | None
        """
        # 정규화된 키로 조회
        # 예: "대한항공:macbook pro" → "korean_air:macbook_pro"
        pass

    @abstractmethod
    async def get_all_rules(self) -> list[dict]:
        """모든 규칙 조회.

        Returns:
            [
                {
                    "item_key": str,
                    "display_name": str,
                    "aliases": list[str],
                    "unit": str,
                    "carry_on_rule": dict,
                    "checked_rule": dict,
                    "tips": str | None
                },
                ...
            ]
        """
        pass