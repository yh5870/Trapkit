"""Database Dependencies."""

from .repositories import (
    TripRepositoryDep,
    get_trip_repository,
    ItemRepositoryDep,
    get_item_repository,
    MemoRepositoryDep,
    get_memo_repository,
)

__all__ = [
    "TripRepositoryDep",
    "get_trip_repository",
    "ItemRepositoryDep",
    "get_item_repository",
    "MemoRepositoryDep",
    "get_memo_repository",
]

# 수화물 규정 캐시 클라이언트 (외부 의존성 주입)
BaggageCacheClientDep: None


def get_baggage_cache_client() -> "BaggageCacheClientDep":
    """수화물 규정 캐시 클라이언트 의존성 주입 (Lazily 초기화)

    Returns:
        의존성 주입 함수

    Use case:
        @router.get("/api/v1/baggage/check")
        async def check_baggage(
            cache_client: BaggageCacheClient = Depends(get_baggage_cache_client),
            ...
        ):
            rule = await cache_client.get_cached_rule(...)
    """
    async def _lazy_init() -> BaggageCacheClientDep:
        from infrastructure.external.redis_baggage_client import BaggageCacheClient

        # 싱글톤 패턴으로 전역 변수 할당
        import infrastructure.external.redis_baggage_client as module
        global BaggageCacheClientDep
        if BaggageCacheClientDep is None:
            BaggageCacheClientDep = module.BaggageRuleCacheClient()
        return BaggageCacheClientDep

    return _lazy_init()
