"""수화물 규정 캐시 Redis 클라이언트

수화물 규정 검증 결과를 캐싱하여 DB 쿼리 절감
"""

import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from app.core.redis import cache_get, cache_set, cache_delete


class BaggageRuleCacheClient:
    """수화물 규정 캐시 클라이언트"""

    def __init__(self):
        """캐시 설정 초기화

        캐시 키 접두사: baggage
        TTL: 7일 (604800초)
        """
        self.base_key = "baggage"
        self.ttl = 604800  # 7일
        self.default_expiration = datetime.utcnow() + timedelta(days=7)

    def generate_cache_key(
        self,
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None
    ) -> str:
        """수화물 규정 캐시 키 생성

        Args:
            airline: 항공사명
            product: 제품명
            value: 크기/용량 (선택)
            unit: 단위 (선택)

        Returns:
            캐시 키 (형식: baggage:{정규화_항공사}:{정규화_제품명}:{값}:{단위})

        Examples:
            >>> client = BaggageRuleCacheClient()
            >>> client.generate_cache_key("korean air", "맥북", 15.6, "인치")
            "baggage:대한항공:노트북:15.6:인치"
            >>> client.generate_cache_key("아시아나", "laptop")
            "baggage:아시아나항공:노트북::"
        """
        # normalizer import는 런타임에 호출하여 순환 참조 방지
        from shared.utils.normalizer import normalize_airline, normalize_product, generate_baggage_cache_key

        # 정규화된 항공사/제품명으로 캐시 키 생성
        return generate_baggage_cache_key(airline, product, value, unit)

    async def get_cached_rule(
        self,
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None
    ) -> Optional[Dict[str, Any]]:
        """캐시된 규칙 조회

        Args:
            airline: 항공사명
            product: 제품명
            value: 크기/용량 (선택)
            unit: 단위 (선택)

        Returns:
            캐시된 규칙 (cache miss 시 None)

        Examples:
            >>> client = BaggageRuleCacheClient()
            >>> rule = await client.get_cached_rule("korean air", "맥북")
            # 캐시 히트 시:
            # {
            #     "item_key": "laptop",
            #     "carry_on_rule": {...},
            #     "checked_rule": {...}
            # }
        """
        key = self.generate_cache_key(airline, product, value, unit)
        cached = await cache_get(key)

        if cached:
            try:
                return json.loads(cached)
            except (json.JSONDecodeError, TypeError):
                # 캐시된 데이터가 깨졌으면 삭제
                await cache_delete(key)
                return None

        return None

    async def cache_rule(
        self,
        rule: Dict[str, Any],
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None
    ) -> None:
        """규칙 데이터 캐싱

        Args:
            rule: 규칙 데이터 (DB에서 조회한 결과)
            airline: 항공사명
            product: 제품명
            value: 크기/용량 (선택)
            unit: 단위 (선택)

        Examples:
            >>> client = BaggageRuleCacheClient()
            >>> rule = {"item_key": "laptop", "carry_on_rule": {...}, "checked_rule": {...}}
            >>> await client.cache_rule(rule, "korean air", "맥북")
        """
        key = self.generate_cache_key(airline, product, value, unit)
        await cache_set(key, json.dumps(rule), ttl=self.ttl)

    async def invalidate_rule(
        self,
        airline: str,
        product: str,
        value: float | None = None,
        unit: str | None = None
    ) -> None:
        """특정 규칙 캐시 무효화

        Args:
            airline: 항공사명
            product: 제품명
            value: 크기/용량 (선택)
            unit: 단위 (선택)

        Use case:
            - 규칙이 업데이트될 때
            - 캐시 데이터가 잘못되었을 때
        """
        key = self.generate_cache_key(airline, product, value, unit)
        await cache_delete(key)

    async def invalidate_all_airline_rules(self, airline: str) -> int:
        """특정 항공사의 모든 규칙 캐시 무효화

        Args:
            airline: 항공사명

        Returns:
            무효화된 캐시 키 개수

        Use case:
            - 항공사 규정 전체 변경 시
            - 캐시 무효화 버튼 클릭 시

        Note:
            이 메서드는 Redis KEYS 명령어를 사용하여 패턴 매칭 삭제
        """
        from app.core.redis import get_redis

        client = await get_redis()
        if not client:
            return 0

        # 항공사 정규화
        from shared.utils.normalizer import normalize_airline
        normalized_airline = normalize_airline(airline)

        # 패턴: baggage:{정규화_항공사}:*
        pattern = f"{self.base_key}:{normalized_airline}:*"

        # KEYS 명령으로 패턴 매칭 조회
        keys = []
        async for key in client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            # 일 삭제
            await client.delete(*keys)

        return len(keys)

    async def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보 조회

        Returns:
            {
                "total_keys": int,      # 전체 캐시 키 개수
                "baggage_keys": int,   # 수화물 규정 캐시 키 개수
                "ttl_days": int,         # TTL (일)
                "memory_usage": str     # 메모리 사용량 (approx)
            }
        """
        from app.core.redis import get_redis

        client = await get_redis()
        if not client:
            return {
                "total_keys": 0,
                "baggage_keys": 0,
                "ttl_days": self.ttl // 86400,
                "memory_usage": "N/A"
            }

        # 전체 키 개수
        total_keys = 0
        baggage_keys = 0

        async for key in client.scan_iter(match=f"{self.base_key}:*"):
            total_keys += 1
            baggage_keys += 1

        # 메모리 사용량 (대략 추정)
        memory_usage_bytes = total_keys * 1024  # 각 키당 약 1KB 가정
        memory_usage_mb = memory_usage_bytes / 1024 / 1024

        return {
            "total_keys": total_keys,
            "baggage_keys": baggage_keys,
            "ttl_days": self.ttl // 86400,
            "memory_usage": f"{memory_usage_mb:.1f}MB"
        }

    def is_cache_hit(self, cached_data: Optional[Dict[str, Any]]) -> bool:
        """캐시 히트 여부 확인

        Args:
            cached_data: get_cached_rule()의 반환값

        Returns:
            True: 캐시 히트
            False: 캐시 미스
        """
        return cached_data is not None

    def calculate_cache_hit_rate(
        self,
        total_requests: int,
        cache_hits: int
    ) -> float:
        """캐시 적중률 계산

        Args:
            total_requests: 전체 요청 수
            cache_hits: 캐시 히트 수

        Returns:
            캐시 적중률 (0.0 ~ 1.0)
        """
        if total_requests == 0:
            return 0.0
        return cache_hits / total_requests


# 전역 인스턴스 (싱글톤 패턴)
_baggage_cache_client: BaggageRuleCacheClient | None = None


def get_baggage_cache_client() -> BaggageRuleCacheClient:
    """수화물 규정 캐시 클라이언트 반환 (싱글톤 패턴)

    Returns:
        BaggageRuleCacheClient 인스턴스

    Examples:
        >>> client = get_baggage_cache_client()
        >>> rule = await client.get_cached_rule("korean air", "맥북")
    """
    global _baggage_cache_client
    if _baggage_cache_client is None:
        _baggage_cache_client = BaggageRuleCacheClient()
    return _baggage_cache_client