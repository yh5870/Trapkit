"""SQLAlchemyBaggageRuleRepository 구현."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.domain.repositories.baggage_rule_repository import BaggageRuleRepository
from infrastructure.database.models.baggage_rule_model import BaggageRuleModel


class SQLAlchemyBaggageRuleRepository(BaggageRuleRepository):
    """BaggageRuleRepository의 SQLAlchemy 구현."""

    def __init__(self, session: AsyncSession):
        """초기화.

        Args:
            session: 비동기 SQLAlchemy 세션
        """
        self.session = session

    async def find_by_key(self, item_key: str) -> dict | None:
        """키로 규칙 조회.

        Args:
            item_key: 항목 키 (예: "laptop", "power_bank")

        Returns:
            규칙 딕셔너리 또는 None
        """
        query = select(BaggageRuleModel).where(
            BaggageRuleModel.item_key == item_key
        )

        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return model.to_dict()

    async def find_by_normalized_key(self, normalized_key: str) -> dict | None:
        """정규화된 키로 규칙 조회.

        Args:
            normalized_key: 정규화된 항목 키 (예: "korean_air:laptop")

        Returns:
            규칙 딕셔너리 또는 None
        """
        # 정규화된 키에서 item_key 추출
        # 예: "korean_air:laptop" → "laptop"
        if ":" in normalized_key:
            parts = normalized_key.split(":")
            if len(parts) >= 2:
                # 항공사와 제품이 있는 경우 제품명만 사용
                item_key = parts[-1].lower()
            else:
                # 항공사만 있는 경우 전체를 항공사로 처리
                item_key = parts[0].lower()
        else:
            item_key = normalized_key.lower()

        # 정확히 일치하는 것 먼저 찾기
        query = select(BaggageRuleModel).where(
            BaggageRuleModel.item_key == item_key
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is not None:
            return model.to_dict()

        # 별칭(aliases)에서 찾기
        # 모든 규칙을 가져와서 별칭 비교
        all_rules_query = select(BaggageRuleModel)
        result = await self.session.execute(all_rules_query)
        all_models = result.scalars().all()

        for rule_model in all_models:
            aliases = rule_model.aliases
            if isinstance(aliases, list):
                if any(
                    item_key in alias.lower() or alias.lower() in item_key
                    for alias in aliases
                ):
                    return rule_model.to_dict()

        return None

    async def get_all_rules(self) -> list[dict]:
        """모든 규칙 조회.

        Returns:
            규칙 딕셔너리 목록
        """
        query = select(BaggageRuleModel).order_by(BaggageRuleModel.item_key)
        result = await self.session.execute(query)
        models = result.scalars().all()

        return [model.to_dict() for model in models]