"""수화물 체커 API."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import SessionDep, OptionalUserDep
from app.schemas.baggage import BaggageCheckRequest, BaggageCheckResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/check", response_model=BaggageCheckResponse)
async def check_baggage(body: BaggageCheckRequest, user: OptionalUserDep, db: SessionDep):
    """수화물 판정."""
    # TODO: 규칙 DB 매칭 또는 AI 판정
    # result = await baggage_checker.check(body.item, body.value, body.unit, body.flight_type)
    logger.info(f"수화물 판정 요청: {body.item}, {body.value}{body.unit}, {body.flight_type}")

    # 임시 응답
    return BaggageCheckResponse(
        item=body.item,
        normalized_key="power_bank",
        converted="74Wh",
        carry_on={
            "verdict": "allowed",
            "label": "가능 ○",
            "reason": "100Wh 이하 리튬이온 배터리는 기내 반입이 가능합니다.",
        },
        checked={
            "verdict": "forbidden",
            "label": "불가 ✕",
            "reason": "리튬이온 배터리는 화재 위험 때문에 위탁 수화물에 넣을 수 없습니다.",
        },
        tips="160Wh 초과는 운송 자체가 불가합니다.",
        source="rule_db",
        reference="국토교통부 항공보안 고시",
    )