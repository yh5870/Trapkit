"""수화물 체커 API 라우터."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services.baggage_service import BaggageService
from app.utils.logger import setup_logger
from infrastructure.database.dependencies import (
    get_baggage_rule_repository,
    BaggageCacheClientDep,
)
from interfaces.api.dependencies.auth import get_current_user_id
from interfaces.api.v1.schemas.baggage import (
    BaggageCheckRequest,
    BaggageCheckResponse,
    VerdictResponse,
)
from shared.config.database import get_db

logger = setup_logger(__name__)

router = APIRouter(prefix="/baggage", tags=["Baggage"])


@router.post("/check", response_model=BaggageCheckResponse)
async def check_baggage(
    request: BaggageCheckRequest,
    cache_client: BaggageCacheClientDep,
    db: AsyncSession = Depends(get_db),
    current_user_id: Optional[str] = Depends(get_current_user_id),
):
    """수화물 규정 체크.

    항공사별 수화물 규정을 체크하여 기내 반입 및 위탁 반입 가능 여부를 판정합니다.

    **인증:** 필요

    **요청 본문:**
    ```json
    {
      "airline": "대한항공",
      "product": "맥북",
      "value": 15.6,
      "unit": "inch"
    }
    ```

    **응답 본문:**
    ```json
    {
      "carry_on": {
        "verdict": "allowed",
        "label": "가능 ○",
        "reason": "기내 반입 가능: 15.6inch",
        "emoji": "✅",
        "color_code": "#10b981",
        "is_allowed": true,
        "is_forbidden": false
      },
      "checked": {
        "verdict": "allowed",
        "label": "가능 ○",
        "reason": "위탁 반입 가능: 15.6inch",
        "emoji": "✅",
        "color_code": "#10b981",
        "is_allowed": true,
        "is_forbidden": false
      },
      "checked_at": "2026-07-23T10:30:00"
    }
    ```

    **예외:**
    - 401: 인증되지 않은 사용자
    - 422: 유효하지 않은 단위 (예: "invalid_unit")
    """
    try:
        # 로깅
        logger.info(
            f"수화물 체크 요청: "
            f"airline={request.airline}, product={request.product}, "
            f"value={request.value}, unit={request.unit}, "
            f"user_id={current_user_id}"
        )

        # 캐시 확인
        cached_rule = await cache_client.get_cached_rule(
            airline=request.airline,
            product=request.product,
            value=request.value,
            unit=request.unit,
        )

        # BaggageService 생성
        baggage_repo = get_baggage_rule_repository(db)
        baggage_service = BaggageService(baggage_repo)

        # 수화물 체크 (캐시 사용)
        carry_on_verdict, checked_verdict = await baggage_service.check(
            airline=request.airline,
            product=request.product,
            value=request.value,
            unit=request.unit,
            cached_rules={"cached": cached_rule} if cached_rule else None,
        )

        # 캐시 미스인 경우 DB 조회 후 캐싱
        if not cached_rule:
            # DB에서 규칙 조회 (이미 baggage_service.check에서 수행됨)
            # 여기서는 실제 규칙을 다시 가져와서 캐싱
            from shared.utils.normalizer import normalize_airline, normalize_product, generate_baggage_cache_key

            normalized_key = generate_baggage_cache_key(
                request.airline, request.product, request.value, request.unit
            )

            # DB에서 규칙 조회
            rule = await baggage_repo.find_by_key(normalized_key.split(":")[2])

            if rule:
                # 규칙 캐싱
                await cache_client.cache_rule(
                    rule,
                    airline=request.airline,
                    product=request.product,
                    value=request.value,
                    unit=request.unit,
                )
                logger.info(f"규칙 캐싱 완료: {normalized_key}")
            else:
                logger.warning(f"규칙 없음: {normalized_key}")
        else:
            logger.info(f"캐시 히트: {request.airline}/{request.product}")

        # 응답 변환
        return BaggageCheckResponse(
            carry_on=VerdictResponse.from_domain(carry_on_verdict),
            checked=VerdictResponse.from_domain(checked_verdict),
        )

    except ValueError as e:
        # 유효하지 않은 단위
        logger.warning(f"잘못된 단위: {request.unit}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    except Exception as e:
        # 기타 오류
        logger.error(f"수화물 체크 오류: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"수화물 체크 오류: {str(e)}",
        )