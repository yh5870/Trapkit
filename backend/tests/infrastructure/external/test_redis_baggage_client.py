"""수화물 규정 캐시 클라이언트 테스트"""

import json
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

import pytest
from infrastructure.external.redis_baggage_client import (
    BaggageRuleCacheClient,
    get_baggage_cache_client,
    _baggage_cache_client
)


@pytest.fixture
def mock_redis_pool():
    """Redis 연결 풀 Mock"""
    pool = AsyncMock()
    pool.get = AsyncMock(return_value=MagicMock(decode_responses=True))
    return pool


@pytest.fixture
def mock_redis_client(mock_redis_pool):
    """Redis 클라이언트 Mock"""
    async def mock_get_redis():
        if not mock_redis_pool.get.return_value:
            return None
        mock_redis = MagicMock()
        mock_redis.get = AsyncMock()
        return mock_redis

    return mock_get_redis


class TestBaggageRuleCacheClientInit:
    """캐시 클라이언트 초기화 테스트"""

    def test_init_default_values(self):
        """기본값 확인"""
        client = BaggageRuleCacheClient()

        assert client.base_key == "baggage"
        assert client.ttl == 604800  # 7일
        assert isinstance(client.default_expiration, datetime)


class TestGenerateCacheKey:
    """캐시 키 생성 테스트"""

    def test_generate_cache_key_basic(self):
        """기본 캐시 키 생성"""
        client = BaggageCacheClient()
        key = client.generate_cache_key("korean air", "맥북")

        assert key == "baggage:대한항공:노트북::"

    def test_generate_cache_key_with_value(self):
        """값 포함 캐시 키 생성"""
        client = BaggageCacheClient()
        key = client.generate_cache_key("korean air", "맥북", 15.6, "인치")

        parts = key.split(":")
        assert parts[0] == "baggage"
        assert parts[1] == "대한항공"
        assert parts[2] == "노트북"
        assert parts[3] == "15.6"
        assert parts[4] == "인치"

    def test_generate_cache_key_with_unit(self):
        """단위 포함 캐시 키 생성"""
        client = BaggageCacheClient()
        key = client.generate_cache_key("korean air", "보조배터리", 100, "Wh")

        parts = key.split(":")
        assert parts[0] == "baggage"
        assert parts[1] == "대한항공"
        assert parts[2] == "보조배터리"
        assert parts[3] == "100"
        assert parts[4] == "Wh"

    def test_generate_cache_key_normalized_names(self):
        """정규화된 이름 사용 시 캐시 키 확인"""
        client = BaggageCacheClient()
        key = client.generate_cache_key("KAL", "MACBOOK")

        assert "대한항공" in key
        assert "노트북" in key

    def test_generate_cache_key_parts_count(self):
        """캐시 키 파트 개수 확인"""
        client = BaggageCacheClient()

        # 기본 (항공사, 제품)
        key1 = client.generate_cache_key("korean air", "맥북")
        assert len(key1.split(":")) == 4

        # 항공사, 제품, 값
        key2 = client.generate_cache_key("korean air", "맥북", 15.6)
        assert len(key2.split(":")) == 4

        # 항공사, 제품, 값, 단위
        key3 = client.generate_cache_key("korean air", "맥북", 15.6, "인치")
        assert len(key3.split(":")) == 5


class TestGetCachedRule:
    """캐시된 규칙 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_cached_rule_hit(self, mock_redis_client):
        """캐시 히트 시 규칙 반환"""
        # Mock 설정
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps({
            "item_key": "laptop",
            "display_name": "노트북",
            "carry_on_rule": {"max_size": "16x9x9"},
            "checked_rule": {"max_size": None}
        }))
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.cache_get", return_value=mock_redis.get):
            client = BaggageCacheClient()
            rule = await client.get_cached_rule("korean air", "맥북")

            assert rule is not None
            assert rule["item_key"] == "laptop"
            assert rule["display_name"] == "노트북"

    @pytest.mark.asyncio
    async def test_get_cached_rule_miss(self, mock_redis_client):
        """캐시 미스 시 None 반환"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.cache_get", return_value=mock_redis.get):
            client = BaggageCacheClient()
            rule = await client.get_cached_rule("korean air", "맥북")

            assert rule is None

    @pytest.mark.asyncio
    async def test_get_cached_rule_invalid_json(self, mock_redis_client):
        """잘못된 JSON 데이터 삭제 후 None 반환"""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value="invalid json")
        mock_redis.delete = AsyncMock()
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.cache_get", return_value=mock_redis.get), \
             patch("infrastructure.external.redis_baggage_client.cache_delete", return_value=mock_redis.delete):
            client = BaggageCacheClient()
            rule = await client.get_cached_rule("korean air", "맥북")

            # 캐시 삭제가 호출되어야 함
            mock_redis.delete.assert_called_once()
            assert rule is None


class TestCacheRule:
    """규칙 캐싱 테스트"""

    @pytest.mark.asyncio
    async def test_cache_rule_success(self, mock_redis_client):
        """규칙 캐싱 성공"""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        mock_redis_client.return_value = mock_redis

        rule_data = {
            "item_key": "power_bank",
            "display_name": "보조배터리",
            "carry_on_rule": {"max_wh": 100},
            "checked_rule": {"max_wh": 160}
        }

        with patch("infrastructure.external.redis_baggage_client.cache_set", return_value=mock_redis.set):
            client = BaggageCacheClient()
            await client.cache_rule(rule_data, "korean air", "보조배터리", None, None)

            # 캐시 설정이 호출되어야 함
            mock_redis.set.assert_called_once()
            # JSON 직렬화가 되어야 함
            cached_data = mock_redis.set.call_args[0][1]
            assert json.loads(cached_data) == rule_data

    @pytest.mark.asyncio
    async def test_cache_rule_with_value(self, mock_redis_client):
        """값과 단위 포함 캐시"""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        mock_redis_client.return_value = mock_redis

        rule_data = {"item_key": "laptop"}

        with patch("infrastructure.external.redis_baggage_client.cache_set", return_value=mock_redis.set):
            client = BaggageCacheClient()
            await client.cache_rule(rule_data, "korean air", "맥북", 15.6, "인치")

            # 캐시 설정이 호출되어야 함
            mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cache_rule_sets_ttl(self, mock_redis_client):
        """TTL이 7일로 설정되었는지 확인"""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()
        mock_redis_client.return_value = mock_redis

        client = BaggageCacheClient()
        rule_data = {"item_key": "test"}

        with patch("infrastructure.external.redis_baggage_client.cache_set", return_value=mock_redis.set):
            await client.cache_rule(rule_data, "korean air", "맥북", None, None)

            # TTL 604800초 (7일)로 설정되어야 함
            ttl_arg = mock_redis.set.call_args[3]
            assert ttl_arg == 604800


class TestInvalidateRule:
    """특정 규칙 캐시 무효화 테스트"""

    @pytest.mark.asyncio
    async def test_invalidate_rule_success(self, mock_redis_client):
        """규칙 캐시 무효화 성공"""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock()
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.cache_delete", return_value=mock_redis.delete):
            client = BaggageCacheClient()
            await client.invalidate_rule("korean air", "맥북")

            # 캐시 삭제가 호출되어야 함
            mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    async def test_invalidate_rule_with_value(self, mock_redis_client):
        """값과 단위 포함 무효화"""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock()
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.cache_delete", return_value=mock_redis.delete):
            client = BaggageCacheClient()
            await client.invalidate_rule("korean air", "보조배터리", 100, "Wh")

            # 캐시 삭제가 호출되어야 함
            mock_redis.delete.assert_called_once()


class TestInvalidateAllAirlineRules:
    """특정 항공사 전체 규칙 캐시 무효화 테스트"""

    @pytest.mark.asyncio
    async def test_invalidate_all_airline_rules_success(self, mock_redis_client):
        """항공사 전체 규칙 캐시 무효화 성공"""
        mock_redis = AsyncMock()
        mock_scan_iter = AsyncMock()
        mock_redis_delete = AsyncMock()

        # KEYS 명령으로 패턴 매칭 조회 시 결과
        async def scan_iter_mock(match):
            keys = ["baggage:대한항공:laptop:", "baggage:대한항공:tablet:"]
            for key in keys:
                yield key

        mock_redis.scan_iter = AsyncMock(side_effect=scan_iter_mock)
        mock_redis.delete = AsyncMock()
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.get_redis", return_value=mock_redis_client), \
             patch("infrastructure.external.redis_baggage_client.cache_delete", return_value=mock_redis_delete):
            client = BaggageCacheClient()
            count = await client.invalidate_all_airline_rules("korean air")

            # KEYS 명령이 호출되어야 함
            mock_redis_client.return_value.scan_iter.assert_called_once()
            # delete가 2번 호출되어야 함 (2개 키)
            assert mock_redis_delete.call_count == 2

            # 정확히 2개 키가 삭제되어야 함
            assert count == 2


class TestGetCacheStats:
    """캐시 통계 정보 조회 테스트"""

    @pytest.mark.asyncio
    async def test_get_cache_stats_success(self, mock_redis_client):
        """캐시 통계 조회 성공"""
        mock_redis = AsyncMock()
        mock_scan_iter = AsyncMock()

        # 2개 수화물 규칙 캐시 (baggage:대한항공:laptop:, baggage:대한항공:tablet:)
        async def scan_iter_mock(match):
            keys = ["baggage:대한항공:laptop:", "baggage:대한항공:tablet:", "other_key:123"]
            for key in keys:
                yield key

        mock_redis.scan_iter = AsyncMock(side_effect=scan_iter_mock)
        mock_redis_client.return_value = mock_redis

        with patch("infrastructure.external.redis_baggage_client.get_redis", return_value=mock_redis_client):
            client = BaggageRuleCacheClient()
            stats = await client.get_cache_stats()

            # 통계 확인
            assert stats["total_keys"] == 3
            assert stats["baggage_keys"] == 2
            assert stats["ttl_days"] == 7
            assert stats["memory_usage"] != "N/A"

    @pytest.mark.asyncio
    async def test_get_cache_stats_no_redis(self, mock_redis_client):
        """Redis 연결 없을 때 빈 통계 반환"""
        mock_redis_client.return_value = None

        with patch("infrastructure.external.redis_baggage_client.get_redis", return_value=lambda: None):
            client = BaggageCacheClient()
            stats = await client.get_cache_stats()

            assert stats["total_keys"] == 0
            assert stats["baggage_keys"] == 0
            assert stats["ttl_days"] == 7
            assert stats["memory_usage"] == "N/A"


class TestIsCacheHit:
    """캐시 히트 여부 확인 테스트"""

    def test_is_cache_hit_hit(self):
        """캐시 히트"""
        client = BaggageCacheClient()

        cached_data = {"item_key": "laptop"}
        assert client.is_cache_hit(cached_data) is True

    def test_is_cache_hit_miss(self):
        """캐시 미스"""
        client = BaggageCacheClient()

        assert client.is_cache_hit(None) is False
        assert client.is_cache_hit({}) is False


class TestCalculateCacheHitRate:
    """캐시 적중률 계산 테스트"""

    def test_calculate_cache_hit_rate_zero_requests(self):
        """요청이 0개일 때 0.0 반환"""
        client = BaggageRuleCacheClient()
        rate = client.calculate_cache_hit_rate(0, 0)
        assert rate == 0.0

    def test_calculate_cache_hit_rate_all_hits(self):
        """모두 캐시 히트 시 1.0 반환"""
        client = BaggageRuleCacheClient()
        rate = client.calculate_cache_hit_rate(10, 10)
        assert rate == 1.0

    def test_calculate_cache_hit_rate_half_hits(self):
        """절반 캐시 히트 시 0.5 반환"""
        client = BaggageRuleCacheClient()
        rate = client.calculate_cache_hit_rate(10, 5)
        assert rate == 0.5

    def test_calculate_cache_hit_rate_no_hits(self):
        """모두 캐시 미스일 때 0.0 반환"""
        client = BaggageCacheClient()
        rate = client.calculate_cache_hit_rate(10, 0)
        assert rate == 0.0


class TestGetBaggageCacheClient:
    """싱글톤 패턴 함수 테스트"""

    def test_get_baggage_cache_client_returns_singleton(self):
        """싱글톤 패턴 반환 확인"""
        client1 = get_baggage_cache_client()
        client2 = get_baggage_cache_client()

        # 동일한 인스턴스여야 함
        assert client1 is client2

    def test_get_baggage_cache_client_initializes_on_first_call(self):
        """첫 호출 시 초기화되어야 함"""
        global _baggage_cache_client
        _baggage_cache_client = None

        client1 = get_baggage_cache_client()
        assert _baggage_cache_client is not None

        # 이미 초기화되었으니 두 번째 호출은 같은 인스턴스
        client2 = get_baggage_cache_client()
        assert client2 is client1


# 테스트 실행
if __name__ == "__main__":
    pytest.main([__file__, "-v"])