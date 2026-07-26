"""개발 전용 엔드포인트 가드.

인증 없이 동작하는 `/dev` 엔드포인트를 프로덕션에서 차단한다.

이 엔드포인트들은 로컬 개발 편의를 위해 인증을 생략하므로, 프로덕션에
노출되면 누구나 타인의 데이터를 생성/조회할 수 있다. 라우트 정의는
import 시점에 고정되므로 등록 자체를 조건부로 만들기 어려워,
요청 시점에 환경을 확인하는 의존성으로 차단한다.

403이 아니라 404를 반환하는 이유:
403은 "존재하지만 권한 없음"을 알려주어 엔드포인트의 존재를 노출한다.
404는 일반 라우트 미존재와 구분되지 않아 정보를 덜 흘린다.
"""

from fastapi import HTTPException, status

from app.config import settings

# 개발 전용 라우트를 허용할 환경
_ALLOWED_ENVIRONMENTS = {"development", "local", "test"}


async def dev_only() -> None:
    """프로덕션이면 요청을 404로 차단.

    Raises:
        HTTPException: ENVIRONMENT가 개발 환경이 아닐 때 404
    """
    environment = (settings.ENVIRONMENT or "").strip().lower()

    if environment not in _ALLOWED_ENVIRONMENTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )
