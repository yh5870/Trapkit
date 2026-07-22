"""Authentication dependency for API endpoints.

JWT 토큰 검증 및 사용자 식별을 제공합니다.
현재는 Mock 구현으로, 프로덕션에서는 JWKS 연동 필요.
"""

from fastapi import Depends, HTTPException, Header, status


async def get_current_user_id(
    authorization: str | None = Header(None)
) -> str:
    """현재 사용자 ID 반환 (Mock 구현).

    Authorization 헤더에서 토큰을 추출하고 검증합니다.
    현재는 개발용으로 모든 요청에 대해 가짜 사용자 ID를 반환합니다.

    Args:
        authorization: Authorization 헤더 값 (Bearer {token})

    Returns:
        str: 사용자 ID

    Raises:
        HTTPException: Authorization 헤더가 없는 경우

    Note:
        🔄 TODO: JWKS 연동 필요
        - JWKS 키 서버에서 공개 키 조회
        - JWT 서명 검증
        - 토큰 만료 확인
        - 실제 user_id 추출

    Example:
        ```python
        @router.get("/trips")
        async def get_trips(
            user_id: str = Depends(get_current_user_id)
        ):
            return await service.get_user_trips(user_id)
        ```
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Mock: 항상 같은 사용자 ID 반환 (개발용)
    # 실제 구현에서는 토큰 검증 후 실제 user_id 반환
    return "dev-user-id"


async def get_optional_user_id(
    authorization: str | None = Header(None)
) -> str | None:
    """선택적 사용자 ID 반환.

    인증이 필요 없는 엔드포인트에서 사용됩니다.
    토큰이 있으면 user_id 반환, 없으면 None 반환.

    Args:
        authorization: Authorization 헤더 값 (Bearer {token})

    Returns:
        str | None: 사용자 ID 또는 None

    Example:
        ```python
        @router.get("/public/trips")
        async def get_public_trips(
            user_id: str | None = Depends(get_optional_user_id)
        ):
            if user_id:
                # 개인화된 결과
                return await service.get_personalized_trips(user_id)
            else:
                # 공개 결과
                return await service.get_public_trips()
        ```
    """
    if not authorization:
        return None

    # Mock: 항상 같은 사용자 ID 반환
    return "dev-user-id"