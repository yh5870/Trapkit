"""Trip API 통합 테스트.

전체 API 흐름을 검증합니다:
- 인증 → API → Service → Repository → DB
- 성공/실패 시나리오
- 권한 확인
"""

from app.core.security import create_token
import pytest


class TestGetUserTrips:
    """GET /api/v1/trips - 사용자 Trip 목록 조회 테스트."""

    async def test_get_user_trips_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        multiple_test_trips: list,
    ):
        """사용자 Trip 목록 조회 성공."""
        response = test_client.get("/api/v1/trips", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "trips" in data
        assert "total" in data
        assert data["total"] == len(multiple_test_trips)
        assert len(data["trips"]) == len(multiple_test_trips)

        # 첫 번째 Trip 확인
        first_trip = data["trips"][0]
        assert "id" in first_trip
        assert "title" in first_trip
        assert "destination" in first_trip
        assert first_trip["user_id"] == "test-user-123"
        assert "cautions" in first_trip
        assert "baggage_summary" in first_trip

    async def test_get_user_trips_empty(self, test_client, auth_headers: dict[str, str]):
        """사용자 Trip이 없는 경우 빈 목록 반환."""
        response = test_client.get("/api/v1/trips", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["trips"] == []
        assert data["total"] == 0

    async def test_get_user_trips_unauthorized(self, test_client, unauth_headers: dict[str, str]):
        """인증 없이 Trip 목록 조회 시 401."""
        response = test_client.get("/api/v1/trips", headers=unauth_headers)

        assert response.status_code == 401


class TestGetTripById:
    """GET /api/v1/trips/{id} - 단일 Trip 조회 테스트."""

    async def test_get_trip_by_id_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_trip,
    ):
        """ID로 Trip 조회 성공."""
        trip_id = str(test_trip.id.value)
        response = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == trip_id
        assert data["title"] == "테스트 여행"
        assert data["destination"] == "도쿄"
        assert data["user_id"] == "test-user-123"
        assert len(data["cautions"]) == 1
        assert data["cautions"][0]["text"] == "여권 유효기간 확인"
        assert len(data["baggage_summary"]) == 2
        assert any(item["type"] == "carry_on" for item in data["baggage_summary"])
        assert any(item["type"] == "checked" for item in data["baggage_summary"])

    async def test_get_trip_by_id_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Trip ID 조회 시 404."""
        response = test_client.get("/api/v1/trips/00000000-0000-0000-0000-000000000000", headers=auth_headers)

        assert response.status_code == 404
        data = response.json()

        assert "detail" in data

    async def test_get_trip_by_id_unauthorized(self, test_client, unauth_headers: dict[str, str]):
        """인증 없이 Trip 조회 시 401."""
        response = test_client.get("/api/v1/trips/00000000-0000-0000-0000-000000000001", headers=unauth_headers)

        assert response.status_code == 401


class TestCreateTrip:
    """POST /api/v1/trips - Trip 생성 테스트."""

    async def test_create_trip_success(self, test_client, auth_headers: dict[str, str]):
        """Trip 생성 성공."""
        request_data = {
            "title": "새 여행",
            "destination": "파리",
            "purpose": ["미술관", "카페"],
            "duration_nights": 7,
            "departure_month": 10,
            "companions": "연인",
            "cautions": [{"text": "비자 확인"}],
            "baggage_summary": [
                {"type": "carry_on", "items": ["여권", "티켓"]},
                {"type": "checked", "items": ["옷", "신발"]},
            ],
        }

        response = test_client.post("/api/v1/trips", json=request_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["title"] == "새 여행"
        assert data["destination"] == "파리"
        assert data["purpose"] == ["미술관", "카페"]
        assert data["user_id"] == "test-user-123"
        assert len(data["cautions"]) == 1
        assert data["cautions"][0]["text"] == "비자 확인"
        assert "baggage_summary" in data

    async def test_create_trip_minimal(self, test_client, auth_headers: dict[str, str]):
        """최소 필드만으로 Trip 생성."""
        request_data = {
            "title": "최소 여행",
            "destination": "제주",
            "purpose": ["휴양"],
        }

        response = test_client.post("/api/v1/trips", json=request_data, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()

        assert data["title"] == "최소 여행"
        assert data["destination"] == "제주"
        assert data["purpose"] == ["휴양"]

    async def test_create_trip_unauthorized(self, test_client, unauth_headers: dict[str, str]):
        """인증 없이 Trip 생성 시 401."""
        request_data = {
            "title": "무단 여행",
            "destination": "어딘가",
            "purpose": ["탐험"],
        }

        response = test_client.post("/api/v1/trips", json=request_data, headers=unauth_headers)

        assert response.status_code == 401


class TestUpdateTrip:
    """PATCH /api/v1/trips/{id} - Trip 수정 테스트."""

    async def test_update_trip_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_trip,
    ):
        """Trip 수정 성공."""
        trip_id = str(test_trip.id.value)
        request_data = {
            "title": "수정된 여행",
            "duration_nights": 10,
        }

        response = test_client.patch(f"/api/v1/trips/{trip_id}", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == trip_id
        assert data["title"] == "수정된 여행"
        assert data["duration_nights"] == 10
        # 원래 값 유지 확인
        assert data["destination"] == "도쿄"

    async def test_update_trip_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Trip 수정 시 404."""
        request_data = {"title": "수정"}

        response = test_client.patch("/api/v1/trips/00000000-0000-0000-0000-000000000000", json=request_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_update_trip_unauthorized(self, test_client, unauth_headers: dict[str, str]):
        """인증 없이 Trip 수정 시 401."""
        request_data = {"title": "수정"}

        response = test_client.patch("/api/v1/trips/00000000-0000-0000-0000-000000000001", json=request_data, headers=unauth_headers)

        assert response.status_code == 401


class TestDeleteTrip:
    """DELETE /api/v1/trips/{id} - Trip 삭제 테스트."""

    async def test_delete_trip_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_trip,
    ):
        """Trip 삭제 성공."""
        trip_id = str(test_trip.id.value)

        # 삭제 요청
        response = test_client.delete(f"/api/v1/trips/{trip_id}", headers=auth_headers)

        assert response.status_code == 204

        # 삭제 확인
        get_response = test_client.get(f"/api/v1/trips/{trip_id}", headers=auth_headers)
        assert get_response.status_code == 404

    async def test_delete_trip_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Trip 삭제 시 404."""
        response = test_client.delete("/api/v1/trips/00000000-0000-0000-0000-000000000000", headers=auth_headers)

        assert response.status_code == 404

    async def test_delete_trip_unauthorized(self, test_client, unauth_headers: dict[str, str]):
        """인증 없이 Trip 삭제 시 401."""
        response = test_client.delete("/api/v1/trips/00000000-0000-0000-0000-000000000001", headers=unauth_headers)

        assert response.status_code == 401


class TestTripOwnership:
    """Trip 소유권 확인 테스트."""

    async def test_cannot_access_other_user_trip(
        self,
        test_client,
        test_trip,
    ):
        """다른 사용자의 Trip에 접근 시도 시 403."""
        # 다른 사용자로 로그인
        other_token = create_token({"sub": "other-user-id"})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        trip_id = str(test_trip.id.value)

        # 조회 시도
        response = test_client.get(f"/api/v1/trips/{trip_id}", headers=other_headers)
        assert response.status_code == 403

        # 수정 시도
        response = test_client.patch(f"/api/v1/trips/{trip_id}", json={"title": "변경"}, headers=other_headers)
        assert response.status_code == 403

        # 삭제 시도
        response = test_client.delete(f"/api/v1/trips/{trip_id}", headers=other_headers)
        assert response.status_code == 403