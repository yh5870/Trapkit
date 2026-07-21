"""레이트 리밋 서비스."""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.utils.exceptions import RateLimitException


class RateLimitService:
    """레이트 리밋 서비스."""

    def __init__(self) -> None:
        # TODO: Redis로 교체
        self.requests: dict[str, list[datetime]] = defaultdict(list)
        self.window = timedelta(minutes=1)

    async def check(self, key: str, limit: int) -> None:
        """레이트 리밋 체크."""
        now = datetime.utcnow()
        # 윈도우 내 요청만 유지
        self.requests[key] = [t for t in self.requests[key] if t > now - self.window]

        if len(self.requests[key]) >= limit:
            raise RateLimitException(f"Rate limit exceeded: {limit} requests per minute")

        self.requests[key].append(now)


rate_limit_service = RateLimitService()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """레이트 리밋 미들웨어."""

    async def dispatch(self, request: Request, call_next):
        """요청 처리 전 레이트 리밋 체크."""
        # 로그인 여부 확인
        auth_header = request.headers.get("Authorization")
        is_authenticated = auth_header is not None

        key = self._get_key(request, is_authenticated)
        limit = settings.RATE_LIMIT_AUTHENTICATED if is_authenticated else settings.RATE_LIMIT_ANONYMOUS

        try:
            await rate_limit_service.check(key, limit)
        except RateLimitException as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e),
            )

        response = await call_next(request)
        return response

    def _get_key(self, request: Request, is_authenticated: bool) -> str:
        """레이트 리밋 키 생성."""
        if is_authenticated:
            # TODO: 토큰에서 user_id 추출
            return "user:temp-id"
        return f"ip:{request.client.host if request.client else 'unknown'}"