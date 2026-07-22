"""SQLAlchemy Trip Repository 테스트."""

from datetime import datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from infrastructure.database.models.trip_model import TripModel
from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository


@pytest.mark.asyncio
class TestSQLAlchemyTripRepository:
    """SQLAlchemy Trip Repository 테스트."""

    async def test_save_new_trip(self, db_session: AsyncSession):
        """새 Trip 저장 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        trip = Trip.create(
            title="Test Trip",
            destination="Seoul",
            purpose=["여행"],
            user_id="test-user-1",
            duration_nights=3,
            departure_month=12,
        )

        saved_trip = await repo.save(trip)

        assert saved_trip.id == trip.id
        assert saved_trip.title == "Test Trip"
        assert saved_trip.destination == "Seoul"
        assert saved_trip.user_id == "test-user-1"

    async def test_save_update_existing_trip(self, db_session: AsyncSession):
        """기존 Trip 업데이트 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        # 먼저 저장
        trip = Trip.create(
            title="Original Title",
            destination="Busan",
            purpose=["휴가"],
            user_id="test-user-1",
        )
        saved_trip = await repo.save(trip)

        # 업데이트
        updated_trip = saved_trip.update(title="Updated Title")
        result = await repo.save(updated_trip)

        assert result.title == "Updated Title"
        assert result.destination == "Busan"

    async def test_find_by_id(self, db_session: AsyncSession):
        """ID로 Trip 조회 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        trip = Trip.create(
            title="Test Trip",
            destination="Jeju",
            purpose=["관광"],
            user_id="test-user-1",
        )
        saved_trip = await repo.save(trip)

        found_trip = await repo.find_by_id(saved_trip.id)

        assert found_trip is not None
        assert found_trip.id == saved_trip.id
        assert found_trip.title == "Test Trip"

    async def test_find_by_id_not_found(self, db_session: AsyncSession):
        """존재하지 않는 ID로 조회 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        non_existent_id = TripId(uuid4())
        found_trip = await repo.find_by_id(non_existent_id)

        assert found_trip is None

    async def test_find_by_user_id(self, db_session: AsyncSession):
        """사용자 ID로 Trip 목록 조회 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        # 같은 사용자의 여러 Trip 생성
        trip1 = Trip.create(
            title="Trip 1",
            destination="Seoul",
            purpose=["여행"],
            user_id="test-user-1",
        )
        trip2 = Trip.create(
            title="Trip 2",
            destination="Busan",
            purpose=["휴가"],
            user_id="test-user-1",
        )
        trip3 = Trip.create(
            title="Trip 3",
            destination="Jeju",
            purpose=["관광"],
            user_id="test-user-2",  # 다른 사용자
        )

        await repo.save(trip1)
        await repo.save(trip2)
        await repo.save(trip3)

        # test-user-1의 Trip만 조회
        trips = await repo.find_by_user_id("test-user-1")

        assert len(trips) == 2
        assert all(trip.user_id == "test-user-1" for trip in trips)

    async def test_find_by_user_id_empty(self, db_session: AsyncSession):
        """Trip이 없는 사용자 조회 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        trips = await repo.find_by_user_id("non-existent-user")

        assert trips == []

    async def test_delete(self, db_session: AsyncSession):
        """Trip 삭제 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        trip = Trip.create(
            title="To Delete",
            destination="Somewhere",
            purpose=["여행"],
            user_id="test-user-1",
        )
        saved_trip = await repo.save(trip)

        # 삭제
        await repo.delete(saved_trip.id)

        # 삭제 확인
        found_trip = await repo.find_by_id(saved_trip.id)
        assert found_trip is None

    async def test_to_domain_conversion(self, db_session: AsyncSession):
        """ORM 모델 → 도메인 모델 변환 테스트."""
        repo = SQLAlchemyTripRepository(db_session)

        trip = Trip.create(
            title="Test",
            destination="Seoul",
            purpose=["여행"],
            user_id="test-user-1",
            cautions=[{"category": "기후", "text": "춥습니다"}],
            baggage_summary=[{"item": "보조배터리", "rule": "기내 반입만 가능"}],
        )
        saved_trip = await repo.save(trip)

        # 조회하면 도메인 모델로 변환됨
        found_trip = await repo.find_by_id(saved_trip.id)

        assert isinstance(found_trip, Trip)
        assert isinstance(found_trip.id, TripId)
        assert found_trip.cautions == [{"category": "기후", "text": "춥습니다"}]
        assert found_trip.baggage_summary == [{"item": "보조배터리", "rule": "기내 반입만 가능"}]
