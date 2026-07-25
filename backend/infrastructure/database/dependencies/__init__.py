"""Database Dependencies."""

from typing import Annotated, TYPE_CHECKING

from fastapi import Depends

from .repositories import (
    TripRepositoryDep,
    get_trip_repository,
    ItemRepositoryDep,
    get_item_repository,
    MemoRepositoryDep,
    get_memo_repository,
    BaggageRuleRepositoryDep,
    get_baggage_rule_repository,
    UserRepositoryDep,
    get_user_repository,
)

if TYPE_CHECKING:
    from infrastructure.external.redis_baggage_client import BaggageRuleCacheClient

__all__ = [
    "TripRepositoryDep",
    "get_trip_repository",
    "ItemRepositoryDep",
    "get_item_repository",
    "MemoRepositoryDep",
    "get_memo_repository",
    "BaggageRuleRepositoryDep",
    "get_baggage_rule_repository",
    "UserRepositoryDep",
    "get_user_repository",
    "BaggageCacheClientDep",
]


def get_baggage_cache_client() -> "BaggageRuleCacheClient":
    """수화물 규정 캐시 클라이언트 싱글톤 반환 (FastAPI 의존성 주입)

    Returns:
        BaggageRuleCacheClient 인스턴스

    Use case:
        ```python
        @router.post("/check")
        async def check_baggage(
            cache_client: BaggageCacheClientDep,
            ...
        ):
            rule = await cache_client.get_cached_rule("korean air", "맥북")
        ```
    """
    from infrastructure.external.redis_baggage_client import get_baggage_cache_client as _get_cache_client

    return _get_cache_client()


# 타입 별칭 (코드 가독성 향상)
BaggageCacheClientDep = Annotated["BaggageRuleCacheClient", Depends(get_baggage_cache_client)]
