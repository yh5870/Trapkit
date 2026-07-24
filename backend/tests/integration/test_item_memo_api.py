"""Item API 통합 테스트.

전체 API 흐름을 검증합니다:
- 인증 → API → Service → Repository → DB
- Item CRUD 시나리오
- 권한 확인
"""

import pytest


class TestGetItems:
    """GET /api/v1/items/{trip_id} - Item 목록 조회 테스트."""

    async def test_get_items_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        multiple_test_items: list,
    ):
        """Trip ID로 Item 목록 조회 성공."""
        trip_id = str(multiple_test_items[0].trip_id.value)
        response = test_client.get(f"/api/v1/items/{trip_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "trip_id" in data
        assert "items" in data
        assert "total" in data
        assert "checked" in data
        assert "pending" in data
        assert data["total"] == len(multiple_test_items)
        assert len(data["items"]) == len(multiple_test_items)

        # 첫 번째 Item 확인
        first_item = data["items"][0]
        assert "id" in first_item
        assert "category" in first_item
        assert "name" in first_item
        assert "quantity" in first_item
        assert "tip" in first_item
        assert "baggage_flag" in first_item
        assert "source" in first_item
        assert "checked" in first_item
        assert "sort_order" in first_item

    async def test_get_items_empty(self, test_client, auth_headers: dict[str, str], test_trip):
        """Item이 없는 경우 빈 목록 반환."""
        trip_id = str(test_trip.id.value)
        response = test_client.get(f"/api/v1/items/{trip_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["items"] == []
        assert data["total"] == 0
        assert data["checked"] == 0
        assert data["pending"] == 0

    async def test_get_items_trip_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Trip ID 조회 시 404."""
        response = test_client.get("/api/v1/items/00000000-0000-0000-0000-000000000000", headers=auth_headers)

        assert response.status_code == 404

    async def test_get_items_unauthorized(self, test_client, test_trip):
        """인증 없이 Item 목록 조회 시 401."""
        trip_id = str(test_trip.id.value)
        response = test_client.get(f"/api/v1/items/{trip_id}")

        assert response.status_code == 401


class TestCreateItem:
    """POST /api/v1/items - Item 생성 테스트."""

    async def test_create_item_success(self, test_client, auth_headers: dict[str, str], test_trip):
        """Item 생성 성공."""
        trip_id = str(test_trip.id.value)
        request_data = {
            "trip_id": trip_id,
            "category": "의류",
            "name": "바지",
            "quantity": "2벌",
            "tip": "데님으로 준비",
            "baggage_flag": "checked",
            "source": "user",
        }

        response = test_client.post("/api/v1/items", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert data["trip_id"] == trip_id
        assert data["category"] == "의류"
        assert data["name"] == "바지"
        assert data["quantity"] == "2벌"
        assert data["tip"] == "데님으로 준비"
        assert data["baggage_flag"] == "checked"
        assert data["source"] == "user"
        assert "checked" in data
        assert "sort_order" in data

    async def test_create_item_minimal(self, test_client, auth_headers: dict[str, str], test_trip):
        """최소 필드만으로 Item 생성."""
        trip_id = str(test_trip.id.value)
        request_data = {
            "trip_id": trip_id,
            "category": "기타",
            "name": "테스트 아이템",
        }

        response = test_client.post("/api/v1/items", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["category"] == "기타"
        assert data["name"] == "테스트 아이템"

    async def test_create_item_trip_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Trip에 Item 생성 시 404."""
        request_data = {
            "trip_id": "00000000-0000-0000-0000-000000000000",
            "category": "기타",
            "name": "테스트",
        }

        response = test_client.post("/api/v1/items", json=request_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_create_item_unauthorized(self, test_client, test_trip):
        """인증 없이 Item 생성 시 401."""
        trip_id = str(test_trip.id.value)
        request_data = {
            "trip_id": trip_id,
            "category": "기타",
            "name": "테스트",
        }

        response = test_client.post("/api/v1/items", json=request_data)

        assert response.status_code == 401


class TestUpdateItem:
    """PATCH /api/v1/items/{item_id} - Item 수정 테스트."""

    async def test_update_item_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """Item 수정 성공."""
        item_id = str(test_item.id.value)
        request_data = {
            "name": "수정된 여권",
            "quantity": "2개",
            "tip": "수정된 팁",
        }

        response = test_client.patch(f"/api/v1/items/{item_id}", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == item_id
        assert data["name"] == "수정된 여권"
        assert data["quantity"] == "2개"
        assert data["tip"] == "수정된 팁"
        # 원래 값 유지 확인
        assert data["category"] == "여권"

    async def test_update_item_check_toggle(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """Item 체크박스 토글."""
        item_id = str(test_item.id.value)

        # 체크
        request_data = {"checked": True}
        response = test_client.patch(f"/api/v1/items/{item_id}", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["checked"] is True

        # 언체크
        request_data = {"checked": False}
        response = test_client.patch(f"/api/v1/items/{item_id}", json=request_data, headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["checked"] is False

    async def test_update_item_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Item 수정 시 404."""
        request_data = {"name": "수정"}

        response = test_client.patch("/api/v1/items/00000000-0000-0000-0000-000000000000", json=request_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_update_item_unauthorized(self, test_client, test_item):
        """인증 없이 Item 수정 시 401."""
        item_id = str(test_item.id.value)
        request_data = {"name": "수정"}

        response = test_client.patch(f"/api/v1/items/{item_id}", json=request_data)

        assert response.status_code == 401


class TestDeleteItem:
    """DELETE /api/v1/items/{item_id} - Item 삭제 테스트."""

    async def test_delete_item_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """Item 삭제 성공."""
        item_id = str(test_item.id.value)

        # 삭제 요청
        response = test_client.delete(f"/api/v1/items/{item_id}", headers=auth_headers)

        assert response.status_code == 204

        # 삭제 확인 (API로 확인할 방법이 없으므로 404가 아니면 성공)
        # 실제로는 DB에서 직접 확인하거나 조회 API로 확인 필요

    async def test_delete_item_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Item 삭제 시 404."""
        response = test_client.delete("/api/v1/items/00000000-0000-0000-0000-000000000000", headers=auth_headers)

        assert response.status_code == 404

    async def test_delete_item_unauthorized(self, test_client, test_item):
        """인증 없이 Item 삭제 시 401."""
        item_id = str(test_item.id.value)

        response = test_client.delete(f"/api/v1/items/{item_id}")

        assert response.status_code == 401


class TestCheckItem:
    """PATCH /api/v1/items/{item_id}/check - Item 체크박스 테스트."""

    async def test_check_item_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """Item 체크 성공."""
        item_id = str(test_item.id.value)
        request_data = {"checked": True}

        response = test_client.patch(f"/api/v1/items/{item_id}/check", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == item_id
        assert data["checked"] is True

    async def test_uncheck_item_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """Item 언체크 성공."""
        item_id = str(test_item.id.value)
        request_data = {"checked": False}

        response = test_client.patch(f"/api/v1/items/{item_id}/check", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == item_id
        assert data["checked"] is False

    async def test_check_item_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Item 체크 시 404."""
        request_data = {"checked": True}

        response = test_client.patch("/api/v1/items/00000000-0000-0000-0000-000000000000/check", json=request_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_check_item_unauthorized(self, test_client, test_item):
        """인증 없이 Item 체크 시 401."""
        item_id = str(test_item.id.value)
        request_data = {"checked": True}

        response = test_client.patch(f"/api/v1/items/{item_id}/check", json=request_data)

        assert response.status_code == 401


class TestUpdateSortOrder:
    """PATCH /api/v1/items/{item_id}/sort - Item 정렬 순서 변경 테스트."""

    async def test_update_sort_order_success(
        self,
        test_client,
        auth_headers: dict[str, str],
        test_item,
    ):
        """정렬 순서 변경 성공."""
        item_id = str(test_item.id.value)
        request_data = {"new_order": 5}

        response = test_client.patch(f"/api/v1/items/{item_id}/sort", json=request_data, headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == item_id
        assert data["sort_order"] == 5

    async def test_update_sort_order_not_found(self, test_client, auth_headers: dict[str, str]):
        """존재하지 않는 Item 정렬 순서 변경 시 404."""
        request_data = {"new_order": 5}

        response = test_client.patch("/api/v1/items/00000000-0000-0000-0000-000000000000/sort", json=request_data, headers=auth_headers)

        assert response.status_code == 404

    async def test_update_sort_order_unauthorized(self, test_client, test_item):
        """인증 없이 정렬 순서 변경 시 401."""
        item_id = str(test_item.id.value)
        request_data = {"new_order": 5}

        response = test_client.patch(f"/api/v1/items/{item_id}/sort", json=request_data)

        assert response.status_code == 401


class TestItemOwnership:
    """Item 소유권 확인 테스트."""

    async def test_cannot_access_other_user_item(
        self,
        test_client,
        test_item,
    ):
        """다른 사용자의 Item에 접근 시도 시 403."""
        from app.core.security import create_token

        # 다른 사용자로 로그인
        other_token = create_token({"sub": "other-user-id"})
        other_headers = {"Authorization": f"Bearer {other_token}"}

        item_id = str(test_item.id.value)

        # 조회 시도
        response = test_client.patch(f"/api/v1/items/{item_id}", json={"name": "변경"}, headers=other_headers)
        assert response.status_code == 403

        # 삭제 시도
        response = test_client.delete(f"/api/v1/items/{item_id}", headers=other_headers)
        assert response.status_code == 403


# Memo 관련 테스트는 Memo 모델이 구현되면 추가 예정
# 현재 Memo 관련 파일이 누락되어 있어 Item 테스트만 진행
