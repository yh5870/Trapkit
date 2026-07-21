"""Redis 연결."""

from typing import Any

import redis.asyncio as redis
from redis.asyncio import ConnectionPool

from app.config import settings

# Redis 연결 풀
redis_pool: ConnectionPool | None = None


async def get_redis() -> redis.Redis | None:
    """Redis 클라이언트 반환."""
    if not settings.REDIS_URL:
        return None

    global redis_pool
    if redis_pool is None:
        redis_pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

    return redis.Redis(connection_pool=redis_pool)


async def close_redis() -> None:
    """Redis 연결 종료."""
    if redis_pool:
        await redis_pool.disconnect()


async def cache_get(key: str) -> Any | None:
    """캐시에서 값 가져오기."""
    client = await get_redis()
    if not client:
        return None
    value = await client.get(key)
    return value


async def cache_set(key: str, value: Any, ttl: int = 3600) -> None:
    """캐시에 값 설정."""
    client = await get_redis()
    if not client:
        return
    await client.set(key, value, ex=ttl)


async def cache_delete(key: str) -> None:
    """캐시에서 값 삭제."""
    client = await get_redis()
    if not client:
        return
    await client.delete(key)