"""BaggageService 도메인 서비스."""

from typing import Optional

from app.domain.repositories.baggage_rule_repository import BaggageRuleRepository
from app.domain.value_objects.verdict import Verdict, VerdictType


class BaggageService:
    """수화물 체커 도메인 서비스.

    수화물 규정을 체크하여 기내 반입 및 위탁 물로 반입 가능 여부를 판정합니다.
    """

    def __init__(self, rule_repository: BaggageRuleRepository):
        self.rule_repository = rule_repository

    async def check(
        self,
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None,
        cached_rules: dict | None = None,
    ) -> tuple[Verdict, Verdict]:
        """수화물 규정 체크.

        Args:
            airline: 항공사 (예: "대한항공", "아시아나")
            product: 제품명 (예: "맥북 프로", "마우스")
            value: 수량 (예: 15.6 인치)
            unit: 단위 (예: "inch", "cm", "kg")
            cached_rules: 캐싱된 규칙 (선택사항)

        Returns:
            (carry_on_verdict, checked_verdict): 기내 반입, 위탁물로 판정 결과

        Raises:
            ValueError: 유효하지 않은 단위
        """
        # 단위 유효성 검증
        valid_units = {"inch", "cm", "mm", "kg", "g", "mg", "oz", "lb"}
        if unit and unit not in valid_units:
            raise ValueError(f"유효하지 않은 단위: {unit}")

        # 규칙 조회
        rule = await self._find_rule(airline, product, cached_rules)

        if rule is None:
            # 규칙이 없으면 기본값 판정 (보수적)
            return self._get_default_verdict(airline, product)

        # 판정 로직
        carry_on_verdict = self._check_rule(
            rule["carry_on_rule"], value, unit, "carry-on"
        )
        checked_verdict = self._check_rule(
            rule["checked_rule"], value, unit, "checked"
        )

        return carry_on_verdict, checked_verdict

    async def _find_rule(
        self,
        airline: str,
        product: str,
        cached_rules: dict | None = None,
    ) -> dict | None:
        """규칙 조회.

        캐시가 제공되면 사용하고, 없으면 DB에서 조회합니다.
        """
        # 정규화된 키 생성 (항공사 제품명)
        normalized_key = f"{airline.lower()}:{product.lower().replace(' ', '')}"

        # 캐시 확인
        if cached_rules and normalized_key in cached_rules:
            return cached_rules[normalized_key]

        # DB에서 조회
        rule = await self.rule_repository.find_by_key(normalized_key)

        if rule is None:
            # 별명도 시도 별도 규칙 확인 (항공사만으로 조회)
            rule = await self.rule_repository.find_by_key(airline.lower())

        return rule

    def _check_rule(
        self,
        rule: dict,
        value: float | None,
        unit: str | None,
        rule_type: str,
    ) -> Verdict:
        """규칙 판정.

        Args:
            rule: 규칙 데이터
            value: 수량
            unit: 단위
            rule_type: "carry-on" 또는 "checked"

        Returns:
            Verdict 판정 결과
        """
        if not value or not unit:
            # 수량이나 단위가 없으면 "조건부 가능"
            return Verdict(
                verdict=VerdictType.CONDITIONAL,
                reason=f"{rule_type} 규칙: 수량과 단위를 입력해주세요."
            )

        # 단위 변환 (cm → inch, kg → lb 등)
        value_inch = self._convert_to_inches(value, unit)

        # 규칙에 따른 판정
        max_size = rule.get("max_size_cm", 0)  # 최대 크기 (cm)
        max_weight = rule.get("max_weight_kg", 0)  # 최대 무게 (kg)

        if max_size > 0 and value_inch > max_size:
            return Verdict(
                verdict=VerdictType.FORBIDDEN,
                reason=f"크기 초과: {value_inch}인치 > {max_size}cm ({max_size}cm 제한)"
            )

        if max_weight > 0 and self._convert_to_kg(value, unit) > max_weight:
            return Verdict(
                verdict=VerdictType.FORBIDDEN,
                reason=f"무게 초과: {value}{unit} > {max_weight}kg ({max_weight}kg 제한)"
            )

        # 제한 사항 체크
        restrictions = rule.get("restrictions", [])
        if restrictions:
            for restriction in restrictions:
                if restriction.get("category") == "category":
                    if restriction.get("value") == "explosive":
                        return Verdict(
                            verdict=VerdictType.FORBIDDEN,
                            reason="폭발물 금지: 해당 카테고리 반입 불가"
                        )

        return Verdict(
            verdict=VerdictType.ALLOWED,
            reason=f"{rule_type} 반입 가능: {value}{unit}"
        )

    def _convert_to_inches(self, value: float, unit: str) -> float:
        """단위를 inch로 변환."""
        if unit == "cm":
            return value / 2.54
        elif unit == "mm":
            return value / 25.4
        elif unit == "kg":
            return value * 39.37  # approximate
        elif unit == "g":
            return value * 0.03937
        elif unit == "oz":
            return value
        elif unit == "lb":
            return value
        return value  # inch

    def _convert_to_kg(self, value: float, unit: str) -> float:
        """단위를 kg로 변환."""
        if unit == "lb":
            return value / 2.20462
        elif unit == "oz":
            return value / 35.274
        elif unit == "g":
            return value / 1000
        elif unit == "mg":
            return value / 1000000
        elif unit == "inch":
            return value * 0.0254
        elif unit == "cm":
            return value * 0.01
        elif unit == "mm":
            return value * 0.001
        return value  # kg

    def _get_default_verdict(self, airline: str, product: str) -> Verdict:
        """기본 판정 (보수적).

        규칙이 없으면 "조건부 가능"으로 판정.
        """
        return Verdict(
            verdict=VerdictType.CONDITIONAL,
            reason=f"{airline}/{product}: 규칙 정보가 없습니다. 항공사나 제품명을 확인해주세요."
        )