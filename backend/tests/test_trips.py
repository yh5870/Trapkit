"""트립 API 테스트."""

from fastapi import status


async def test_get_trips(client):
    """여행 목록 조회 테스트."""
    response = await client.get("/api/trips")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "trips" in data
    assert isinstance(data["trips"], list)


async def test_generate_trip(client):
    """AI 리스트 생성 테스트."""
    response = await client.post(
        "/api/trips/generate",
        json={
            "destination": "삿포로",
            "purpose": ["스키"],
            "duration_nights": 4,
            "departure_month": 12,
            "companions": "친구 2명",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "trip_title" in data
    assert "categories" in data
    assert "cautions" in data
    assert "baggage_summary" in data


async def test_get_trip_detail(client):
    """여행 상세 조회 테스트."""
    response = await client.get("/api/trips/test-trip-id")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "trip_title" in data


async def test_update_trip(client):
    """여행 제목 수정 테스트."""
    response = await client.patch(
        "/api/trips/test-trip-id",
        json={"title": "수정된 제목"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["trip_title"] == "수정된 제목"


async def test_delete_trip(client):
    """여행 삭제 테스트."""
    response = await client.delete("/api/trips/test-trip-id")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Trip deleted successfully"