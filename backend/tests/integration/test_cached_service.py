"""캐싱 서비스 통합 테스트.

캐싱이 제대로 작동하는지 검증합니다:
- 캐시 미스 시 DB 조회
- 캐시 히트 시 DB 조회 스킵
- 캐시 무효화
"""

from unittest.mock import AsyncMock, patch

import pytest


class TestCachedTripQueryService:
    """CachedTripQueryService 통합 테스트."""

    @pytest.mark.asyncio
    async def test_get_user_trips_cache_miss(self, db_session, multiple_test_trips):
        """캐시 미스 시 DB 조회 후 캐시 저장."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        # 캐시 mock: 첫 호출은 None (캐시 미스), 두 번째 호출은 데이터 반환
        cache_get_mock = AsyncMock(side_effect=[None, "[{\"id\": \"test\"}]"])
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 첫 호출: 캐시 미스 → DB 조회
            trips = await service.get_user_trips("test-user-123")

            # DB에서 조회된 Trip 개수 확인
            assert len(trips) == len(multiple_test_trips)

            # 캐시 저장 호출 확인
            cache_set_mock.assert_called_once()
            call_args = cache_set_mock.call_args
            assert "user_trips:test-user-123" in call_args[0][0]
            assert call_args[0][2] == 3600  # TTL

    @pytest.mark.asyncio
    async def test_get_user_trips_cache_hit(self):
        """캐시 히트 시 DB 조회 스킵."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        # 캐시 mock: 데이터 반환 (캐시 히트)
        cached_data = '[{"id": "cached-trip-id", "title": "캐시된 여행"}]'
        cache_get_mock = AsyncMock(return_value=cached_data)
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 호출: 캐시 히트 → DB 조회 스킵
            trips = await service.get_user_trips("test-user-123")

            # 캐시에서 조회된 데이터 반환 확인
            assert len(trips) == 1
            assert trips[0]["id"] == "cached-trip-id"
            assert trips[0]["title"] == "캐시된 여행"

            # 캐시 저장 호출 안 함 (이미 캐시됨)
            cache_set_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_trip_by_id_cache_miss(self, db_session, test_trip):
        """단일 Trip 조회 캐시 미스 시 DB 조회 후 캐시 저장."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        # 캐시 mock: 첫 호출은 None (캐시 미스)
        cache_get_mock = AsyncMock(return_value=None)
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            trip_id = str(test_trip.id.value)

            # 첫 호출: 캐시 미스 → DB 조회
            trip = await service.get_trip_by_id(trip_id)

            # DB에서 조회된 Trip 확인
            assert trip is not None
            assert trip["id"] == trip_id
            assert trip["title"] == "테스트 여행"

            # 캐시 저장 호출 확인
            cache_set_mock.assert_called_once()
            call_args = cache_set_mock.call_args
            assert f"trip:{trip_id}" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_get_trip_by_id_cache_hit(self):
        """단일 Trip 조회 캐시 히트 시 DB 조회 스킵."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        # 캐시 mock: 데이터 반환 (캐시 히트)
        cached_data = '{"id": "cached-trip-id", "title": "캐시된 여행"}'
        cache_get_mock = AsyncMock(return_value=cached_data)
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 호출: 캐시 히트 → DB 조회 스킵
            trip = await service.get_trip_by_id("cached-trip-id")

            # 캐시에서 조회된 데이터 반환 확인
            assert trip is not None
            assert trip["id"] == "cached-trip-id"
            assert trip["title"] == "캐시된 여행"

            # 캐시 저장 호출 안 함 (이미 캐시됨)
            cache_set_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_trip_by_id_not_found(self, db_session):
        """존재하지 않는 Trip 조회 시 None 반환."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        cache_get_mock = AsyncMock(return_value=None)
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 존재하지 않는 Trip 조회
            trip = await service.get_trip_by_id("non-existent-id")

            # None 반환 확인
            assert trip is None

            # 캐시 저장 호출 안 함 (존재하지 않는 Trip)
            cache_set_mock.assert_not_called()

    @pytest.mark.asyncio
    async def test_invalidate_user_trips_cache(self):
        """사용자 Trip 목록 캐시 무효화."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService

        cache_delete_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_delete", cache_delete_mock):
            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 캐시 무효화 호출
            await service.invalidate_user_trips_cache("test-user-123")

            # 캐시 삭제 호출 확인
            cache_delete_mock.assert_called_once_with("user_trips:test-user-123")

    @pytest.mark.asyncio
    async def test_invalidate_trip_cache(self):
        """특정 Trip 캐시 무효화."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService

        cache_delete_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_delete", cache_delete_mock):
            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 캐시 무효화 호출
            await service.invalidate_trip_cache("trip-123")

            # 캐시 삭제 호출 확인
            cache_delete_mock.assert_called_once_with("trip:trip-123")

    @pytest.mark.asyncio
    async def test_cache_corrupted_data_fallback(self, db_session, multiple_test_trips):
        """캐시 데이터 손상 시 DB 조회로 폴백."""
        from app.application.services.cached_trip_query_service import CachedTripQueryService
        from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository

        # 캐시 mock: 손상된 JSON 반환
        cache_get_mock = AsyncMock(return_value="{invalid json}")
        cache_set_mock = AsyncMock()

        with patch("app.application.services.cached_trip_query_service.cache_get", cache_get_mock), \
             patch("app.application.services.cached_trip_query_service.cache_set", cache_set_mock):

            repo = SQLAlchemyTripRepository(db_session)
            service = CachedTripQueryService(repo)

            # 호출: 캐시 손상 → DB 조회로 폴백
            trips = await service.get_user_trips("test-user-123")

            # DB에서 조회된 Trip 개수 확인
            assert len(trips) == len(multiple_test_trips)

            # 캐시 재저장 호출 확인 (새로운 데이터로)
            cache_set_mock.assert_called_once()


class TestCacheInvalidationFlow:
    """캐시 무효화 흐름 테스트."""

    @pytest.mark.asyncio
    async def test_create_invalidates_cache(self, test_client, auth_headers: dict[str, str]):
        """Trip 생성 후 사용자 Trip 목록 캐시 무효화."""
        # 먼저 목록 조회 (캐시 생성)
        list_response_1 = test_client.get("/api/v1/trips", headers=auth_headers)
        assert list_response_1.status_code == 200

        # Trip 생성
        create_data = {
            "title": "새 여행",
            "destination": "파리",
            "purpose": ["관광"],
        }
        create_response = test_client.post("/api/v1/trips", json=create_data, headers=auth_headers)
        assert create_response.status_code == 201

        # 다시 목록 조회 (캐시 무효화되어 새 Trip 포함)
        list_response_2 = test_client.get("/api/v1/trips", headers=auth_headers)
        assert list_response_2.status_code == 200

        data_2 = list_response_2.json()
        assert data_2["total"] == 1

    @pytest.mark.asyncio
    async def test_update_invalidates_cache(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_trip,
    ):
        """Trip 수정 후 해당 Trip 캐시 무효화."""
        trip_id = str(test_trip.id.value)

        # 먼저 조회 (캐시 생성)
        get_response_1 = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert get_response_1.status_code == 200
        assert get_response_1.json()["title"] == "테스트 여행"

        # Trip 수정
        update_data = {"title": "수정된 여행"}
        update_response = test_client.patch(f"/api/v1/trips/{trip_id}", json=update_data, headers=auth_headers)
        assert update_response.status_code == 201

        # 다시 조회 (캐시 무효화되어 수정된 값 반환)
        get_response_2 = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert get_response_2.status_code == 200
        assert get_response_2.json()["title"] == "수정된 여행"

    @pytest.mark.asyncio
    async def test_delete_invalidates_cache(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_trip,
    ):
        """Trip 삭제 후 해당 Trip 캐시 무효화."""
        trip_id = str(test_trip.id.value)

        # 먼저 조회 (캐시 생성)
        get_response_1 = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert get_response_1.status_code == 200

        # Trip 삭제
        delete_response = test_client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert delete_response.status_code == 204

        # 다시 조회 (캐시 무효화되어 404)
        get_response_2 = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert get_response_2.status_code == 404