"""TripQueryService 단위 테스트."""

from uuid import uuid4

import pytest

from app.application.services.trip_query_service import TripQueryService
from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId


class TestTripQueryService:
    """TripQueryService 테스트."""

    @pytest.fixture
    def mock_repository(self):
        """Mock Repository."""
        from tests.mocks.mock_trip_repository import MockTripRepository

        return MockTripRepository()

    @pytest.fixture
    def service(self, mock_repository):
        """테스트용 서비스."""
        return TripQueryService(mock_repository)

    @pytest.fixture
    def sample_trip(self):
        """샘플 Trip."""
        return Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑", "음식 탐방"],
            user_id="user-123",
            duration_nights=5,
            departure_month=8,
        )

    @pytest.mark.asyncio
    async def test_get_user_trips_returns_user_trips(self, service, mock_repository, sample_trip):
        """사용자의 모든 Trip 조회."""
        # Given: 사용자의 트립 저장
        await mock_repository.save(sample_trip)

        # When: 사용자의 트립 조회
        trips = await service.get_user_trips("user-123")

        # Then
        assert len(trips) == 1
        assert trips[0].title == "도쿄 여행"
        assert trips[0].user_id == "user-123"

    @pytest.mark.asyncio
    async def test_get_user_trips_returns_empty_for_no_trips(self, service):
        """트립이 없으면 빈 리스트 반환."""
        # When: 존재하지 않는 사용자 조회
        trips = await service.get_user_trips("non-existent-user")

        # Then
        assert trips == []

    @pytest.mark.asyncio
    async def test_get_user_trips_filters_by_user_id(self, service, mock_repository):
        """사용자 ID로 필터링."""
        # Given: 두 사용자의 트립 저장
        trip1 = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-1",
        )
        trip2 = Trip.create(
            title="파리 여행",
            destination="프랑스 파리",
            purpose=["관광"],
            user_id="user-2",
        )
        await mock_repository.save(trip1)
        await mock_repository.save(trip2)

        # When: user-1의 트립 조회
        trips = await service.get_user_trips("user-1")

        # Then
        assert len(trips) == 1
        assert trips[0].user_id == "user-1"
        assert trips[0].title == "도쿄 여행"

    @pytest.mark.asyncio
    async def test_get_trip_by_id_returns_trip(self, service, mock_repository, sample_trip):
        """ID로 Trip 조회."""
        # Given: 트립 저장
        await mock_repository.save(sample_trip)
        trip_id_str = str(sample_trip.id.value)

        # When: ID로 조회
        trip = await service.get_trip_by_id(trip_id_str)

        # Then
        assert trip is not None
        assert trip.title == "도쿄 여행"
        assert str(trip.id.value) == trip_id_str

    @pytest.mark.asyncio
    async def test_get_trip_by_id_returns_none_for_nonexistent(self, service):
        """존재하지 않는 ID로 조회 시 None 반환."""
        # Given: 존재하지 않는 UUID
        trip_id_str = str(uuid4())

        # When: 조회
        trip = await service.get_trip_by_id(trip_id_str)

        # Then
        assert trip is None

    @pytest.mark.asyncio
    async def test_get_trip_by_id_converts_string_to_trip_id(self, service, mock_repository, sample_trip):
        """문자열 ID를 TripId로 자동 변환."""
        # Given: 트립 저장
        await mock_repository.save(sample_trip)
        trip_id_str = str(sample_trip.id.value)

        # When: 문자열로 조회
        trip = await service.get_trip_by_id(trip_id_str)

        # Then
        assert trip is not None
        assert isinstance(trip.id, TripId)

    @pytest.mark.asyncio
    async def test_service_uses_repository(self, service, mock_repository, sample_trip):
        """서비스가 Repository를 올바르게 사용."""
        # When: 서비스를 통해 저장
        saved_trip = await service.get_user_trips("user-123")

        # Then: Repository에도 저장됨
        assert len(saved_trip) == 1