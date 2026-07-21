"""수화물 판정 엔진."""

from typing import Any

from app.schemas.baggage import BaggageCheckRequest, BaggageCheckResponse, Verdict


class BaggageChecker:
    """수화물 체커."""

    # TODO: 규칙 DB에서 로드
    RULES_DB = {
        "power_bank": {
            "display_name": "보조배터리",
            "aliases": ["보조밧데리", "power bank", "배터리", "충전기 배터리"],
            "unit": "mah_wh",
            "carry_on_rule": [
                {"max_wh": 100, "verdict": "allowed", "label": "가능 ○", "reason": "100Wh 이하 리튬이온 배터리는 기내 반입이 가능합니다."},
                {"max_wh": 160, "verdict": "conditional", "label": "조건부 △", "reason": "100~160Wh는 항공사 승인 필요, 통상 2개까지."},
            ],
            "carry_on_forbidden": {"verdict": "forbidden", "label": "불가 ✕", "reason": "160Wh 초과는 기내 반입 불가."},
            "checked_rule": {"verdict": "forbidden", "label": "불가 ✕", "reason": "리튬이온 배터리는 화재 위험으로 위탁 불가."},
            "tips": "160Wh 초과는 운송 자체가 불가합니다.",
            "source": "국토교통부 항공보안 고시",
        },
        "sunscreen": {
            "display_name": "선크림",
            "aliases": ["선크림", "sunscreen", "썬크림"],
            "unit": "ml",
            "carry_on_rule": [{"max_ml": 100, "verdict": "allowed", "label": "가능 ○", "reason": "개당 100ml 이하는 기내 반입 가능."}],
            "carry_on_forbidden": {"verdict": "forbidden", "label": "불가 ✕", "reason": "액체류는 개별 용기 100ml 이하만 기내 반입할 수 있습니다."},
            "checked_rule": {"verdict": "allowed", "label": "가능 ○", "reason": "일반 액체류는 위탁 수화물 제한이 없습니다."},
            "tips": "100ml 이하 용기에 소분하면 기내 반입이 가능합니다. 소분 용기들은 1L 이하 투명 지퍼백 1개에 담아야 합니다.",
            "source": "국토교통부 항공보안 고시",
        },
    }

    def __init__(self) -> None:
        # TODO: DB에서 규칙 로드
        pass

    async def check(self, item: str, value: float | None, unit: str, flight_type: str) -> BaggageCheckResponse:
        """수화물 판정."""
        # 1단계: 정규화
        normalized_key = self._normalize(item)
        rule = self._find_rule(normalized_key)

        if rule:
            # 2단계: 규칙 DB 판정
            converted = self._convert_value(value, unit) if value else None
            return self._apply_rule(item, normalized_key, rule, value, unit, converted, flight_type)
        else:
            # 3단계: AI 판정 (폴백)
            return await self._ai_fallback(item, value, unit, flight_type)

    def _normalize(self, item: str) -> str:
        """품목명 정규화."""
        item_lower = item.lower().strip()
        for key, rule in self.RULES_DB.items():
            if item_lower == key or item_lower in rule["aliases"]:
                return key
        return item_lower

    def _find_rule(self, normalized_key: str) -> dict[str, Any] | None:
        """규칙 DB 매칭."""
        return self.RULES_DB.get(normalized_key)

    def _convert_value(self, value: float, unit: str) -> str:
        """값 변환 (mAh → Wh)."""
        if unit == "mAh":
            wh = value * 3.7 / 1000
            return f"{wh:.0f}Wh"
        return f"{value}{unit}"

    def _apply_rule(
        self, item: str, normalized_key: str, rule: dict[str, Any], value: float | None, unit: str, converted: str | None, flight_type: str
    ) -> BaggageCheckResponse:
        """규칙 적용."""
        carry_on = rule["carry_on_forbidden"]
        if value and unit == "mAh":
            wh = value * 3.7 / 1000
            for r in rule["carry_on_rule"]:
                if wh <= r["max_wh"]:
                    carry_on = Verdict(**r)
                    break

        return BaggageCheckResponse(
            item=item,
            normalized_key=normalized_key,
            converted=converted,
            carry_on=carry_on,
            checked=Verdict(**rule["checked_rule"]),
            tips=rule["tips"],
            source="rule_db",
            reference=rule["source"],
        )

    async def _ai_fallback(self, item: str, value: float | None, unit: str, flight_type: str) -> BaggageCheckResponse:
        """AI 판정 폴백."""
        # TODO: 실제 AI 호출
        return BaggageCheckResponse(
            item=item,
            normalized_key=item.lower(),
            converted=f"{value}{unit}" if value else None,
            carry_on=Verdict(
                verdict="conditional",
                label="조건부 △",
                reason="일반적인 기준으로는 조건부 반입 대상입니다. 세부 사양에 따라 달라질 수 있습니다.",
            ),
            checked=Verdict(
                verdict="allowed",
                label="가능 ○",
                reason="일반적인 기준으로는 위탁 가능합니다.",
            ),
            tips="정확한 판정을 위해 용량·사양을 함께 입력해 주세요.",
            source="ai",
            reference="AI 판정",
        )


# 싱글톤 인스턴스
baggage_checker = BaggageChecker()