"""캐싱된 Trip 조회 서비스 테스트."""

from unittest.mock import AsyncMock, patch

import pytest

from app.application.services.cached_trip_query_service import CachedTripQueryService
from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from tests.mocks.mock_trip_repository import MockTripRepository


@pytest.mark.asyncio
class TestCachedTripQueryService:
    """캐싱된 Trip 조회 서비스 테스트."""

    async def test_get_user_trips_with_cache_miss(self):
        """캐시 미스 시 DB 조회 및 캐시 저장 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        # 캐시가 없는 경우 (mock으로 가정)
        with patch("app.application.services.cached_trip_query_service.cache_get") as mock_cache_get:
            with patch("app.application.services.cached_trip_query_service.cache_set") as mock_cache_set:
                mock_cache_get.return_value = None

                trips = await service.get_user_trips("user-1")

                # DB 조회 확인
                assert len(trips) == 0  # Mock repository는 빈 리스트 반환

                # 캐시 저장 확인
                mock_cache_set.assert_called_once()

    async def test_get_user_trips_with_cache_hit(self):
        """캐시 히트 시 캐시에서 반환 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        cached_data = '[{"id": "123", "title": "Cached Trip"}]'

        with patch("app.application.services.cached_trip_query_service.cache_get") as mock_cache_get:
            with patch("app.application.services.cached_trip_query_service.cache_set") as mock_cache_set:
                mock_cache_get.return_value = cached_data

                trips = await service.get_user_trips("user-1")

                # 캐시에서 반환 확인
                assert len(trips) == 1
                assert trips[0]["id"] == "123"

                # 캐시 저장이 호출되지 않아야 함
                mock_cache_set.assert_not_called()

    async def test_get_trip_by_id_with_cache_miss(self):
        """캐시 미스 시 DB 조회 및 캐시 저장 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        with patch("app.application.services.cached_trip_query_service.cache_get") as mock_cache_get:
            with patch("app.application.services.cached_trip_query_service.cache_set") as mock_cache_set:
                mock_cache_get.return_value = None

                trip = await service.get_trip_by_id("trip-1")

                # DB 조회 확인
                assert trip is None  # Mock repository는 None 반환

                # 캐시 저장 확인
                mock_cache_set.assert_called_once()

    async def test_get_trip_by_id_with_cache_hit(self):
        """캐시 히트 시 캐시에서 반환 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        cached_data = '{"id": "123", "title": "Cached Trip"}'

        with patch("app.application.services.cached_trip_query_service.cache_get") as mock_cache_get:
            with patch("app.application.services.cached_trip_query_service.cache_set") as mock_cache_set:
                mock_cache_get.return_value = cached_data

                trip = await service.get_trip_by_id("trip-1")

                # 캐시에서 반환 확인
                assert trip is not None
                assert trip["id"] == "123"

                # 캐시 저장이 호출되지 않아야 함
                mock_cache_set.assert_not_called()

    async def test_invalidate_user_trips_cache(self):
        """사용자 Trip 목록 캐시 무효화 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        with patch("app.application.services.cached_trip_query_service.cache_delete") as mock_cache_delete:
            await service.invalidate_user_trips_cache("user-1")

            # 캐시 삭제 확인
            mock_cache_delete.assert_called_once_with("user_trips:user-1")

    async def test_invalidate_trip_cache(self):
        """Trip 캐시 무효화 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        with patch("app.application.services.cached_trip_query_service.cache_delete") as mock_cache_delete:
            await service.invalidate_trip_cache("trip-1")

            # 캐시 삭제 확인
            mock_cache_delete.assert_called_once_with("trip:trip-1")

    async def test_cache_invalidation_on_trip_update(self):
        """Trip 업데이트 시 캐시 무효화 통합 테스트."""
        mock_repo = MockTripRepository()
        service = CachedTripQueryService(mock_repo)

        # Trip 생성
        trip = Trip.create(
            title="Test Trip",
            destination="Seoul",
            purpose=["여행"],
            user_id="user-1",
        )
        await mock_repo.save(trip)

        # 캐시 무효화
        with patch("app.application.services.cached_trip_query_service.cache_delete") as mock_cache_delete:
            await service.invalidate_user_trips_cache("user-1")
            await service.invalidate_trip_cache(str(trip.id.value))

            # 두 번의 캐시 삭제 호출 확인
            assert mock_cache_delete.call_count == 2
