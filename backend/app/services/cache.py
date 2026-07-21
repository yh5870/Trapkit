"""캐시 서비스 (Redis)."""

from app.core.redis import cache_get, cache_set, cache_delete


class CacheService:
    """캐시 서비스."""

    @staticmethod
    async def get(key: str) -> str | None:
        """캐시에서 값 가져오기."""
        return await cache_get(key)

    @staticmethod
    async def set(key: str, value: str, ttl: int = 3600) -> None:
        """캐시에 값 설정."""
        await cache_set(key, value, ttl)

    @staticmethod
    async def delete(key: str) -> None:
        """캐시에서 값 삭제."""
        await cache_delete(key)

    @staticmethod
    def generate_trip_cache_key(destination: str, purpose: list[str], month: int | None) -> str:
        """트립 캐시 키 생성."""
        purpose_str = ",".join(sorted(purpose))
        return f"trip:{destination}:{purpose_str}:{month or ''}"


cache_service = CacheService()