"""통합 테스트 전용 fixture."""

from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from app.main import app
from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from app.core.security import create_token
from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository
from shared.config.database import get_db


# 테스트용 사용자
TEST_USER = {
    "id": "test-user-123",
    "email": "test@example.com",
    "nickname": "Test Traveler",
}


@pytest.fixture
async def auth_headers() -> dict[str, str]:
    """테스트용 인증 헤더 생성."""
    token = create_token({"sub": TEST_USER["id"]})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_trip(db_session: AsyncSession) -> Trip:
    """테스트용 Trip 생성."""
    trip = Trip.create(
        title="테스트 여행",
        destination="도쿄",
        purpose=["맛집 탐방", "쇼핑"],
        user_id=TEST_USER["id"],
        duration_nights=5,
        departure_month=8,
        companions="가족",
    )
    trip = trip.add_caution("여권 유효기간 확인")
    trip = trip.update_baggage_summary({
        "carry_on": ["여권", "지갑"],
        "checked": ["옷", "화장품"],
    })

    repo = SQLAlchemyTripRepository(db_session)
    return await repo.save(trip)


@pytest.fixture
async def multiple_test_trips(db_session: AsyncSession) -> list[Trip]:
    """여러 개의 테스트용 Trip 생성."""
    trips_data = [
        {
            "title": "서울 여행",
            "destination": "서울",
            "purpose": ["관광", "음식"],
            "duration_nights": 3,
            "departure_month": 9,
            "companions": "친구",
        },
        {
            "title": "부산 여행",
            "destination": "부산",
            "purpose": ["해수욕장"],
            "duration_nights": 2,
            "departure_month": 7,
            "companions": "혼자",
        },
    ]

    repo = SQLAlchemyTripRepository(db_session)
    trips = []

    for data in trips_data:
        trip = Trip.create(
            title=data["title"],
            destination=data["destination"],
            purpose=data["purpose"],
            user_id=TEST_USER["id"],
            duration_nights=data["duration_nights"],
            departure_month=data["departure_month"],
            companions=data["companions"],
        )
        saved_trip = await repo.save(trip)
        trips.append(saved_trip)

    return trips


@pytest.fixture
def test_client(db_session: AsyncSession) -> TestClient:
    """테스트용 HTTP 클라이언트."""
    # DB 세션 오버라이드
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def unauth_headers() -> dict[str, str]:
    """미인증 헤더."""
    return {}