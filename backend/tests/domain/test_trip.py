"""Trip 도메인 모델 단위 테스트."""

from datetime import datetime
from uuid import uuid4

import pytest

from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId


class TestTrip:
    """Trip 엔티티 테스트."""

    def test_create_generates_trip_with_auto_id(self):
        """새 Trip 생성 시 ID 자동 생성."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑", "음식 탐방"],
            user_id="user-123",
        )

        assert trip.id is not None
        assert isinstance(trip.id, TripId)
        assert trip.title == "도쿄 여행"
        assert trip.destination == "일본 도쿄"
        assert trip.purpose == ["쇼핑", "음식 탐방"]
        assert trip.user_id == "user-123"

    def test_create_with_optional_fields(self):
        """선택적 필드 포함하여 Trip 생성."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
            duration_nights=5,
            departure_month=8,
            companions="가족 3인",
        )

        assert trip.duration_nights == 5
        assert trip.departure_month == 8
        assert trip.companions == "가족 3인"

    def test_create_generates_timestamps(self):
        """Trip 생성 시 시간 자동 생성."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        assert trip.created_at is not None
        assert trip.updated_at is not None
        assert isinstance(trip.created_at, datetime)
        assert isinstance(trip.updated_at, datetime)

    def test_create_default_empty_collections(self):
        """기본값으로 빈 컬렉션 생성."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        assert trip.cautions == []
        assert trip.baggage_summary == []

    def test_update_returns_new_instance(self):
        """업데이트 시 새 인스턴스 반환 (불변성)."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        updated_trip = trip.update(title="수정된 제목")

        assert trip is not updated_trip
        assert trip.title == "도쿄 여행"
        assert updated_trip.title == "수정된 제목"

    def test_update_preserves_id_and_user_id(self):
        """업데이트 시 ID와 user_id 보존."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )
        original_id = trip.id

        updated_trip = trip.update(title="수정된 제목")

        assert updated_trip.id == original_id
        assert updated_trip.user_id == "user-123"

    def test_update_updates_timestamp(self):
        """업데이트 시 updated_at 갱신."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )
        original_updated_at = trip.updated_at

        # 시간 지연
        import time
        time.sleep(0.01)

        updated_trip = trip.update(title="수정된 제목")

        assert updated_trip.updated_at > original_updated_at

    def test_update_preserves_created_at(self):
        """업데이트 시 created_at 보존."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )
        original_created_at = trip.created_at

        updated_trip = trip.update(title="수정된 제목")

        assert updated_trip.created_at == original_created_at

    def test_update_none_fields_keep_original(self):
        """None으로 전달된 필드는 원래 값 유지."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
            duration_nights=5,
        )

        updated_trip = trip.update(
            title="수정된 제목",
            destination=None,  # 유지됨
            duration_nights=None,  # 유지됨
        )

        assert updated_trip.title == "수정된 제목"
        assert updated_trip.destination == "일본 도쿄"
        assert updated_trip.duration_nights == 5

    def test_frozen_prevents_mutation(self):
        """불변성 확인."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        with pytest.raises(AttributeError):
            trip.title = "수정된 제목"

    def test_add_caution_adds_to_cautions(self):
        """주의사항 추가."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        caution = {"type": "weather", "message": "비 우산 챙기기"}
        updated_trip = trip.add_caution(caution)

        assert caution in updated_trip.cautions
        assert updated_trip is not trip

    def test_add_caution_preserves_existing_cautions(self):
        """기존 주의사항 보존."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )
        caution1 = {"type": "weather", "message": "비 우산 챙기기"}
        trip_with_caution = trip.add_caution(caution1)

        caution2 = {"type": "document", "message": "여권 확인"}
        updated_trip = trip_with_caution.add_caution(caution2)

        assert caution1 in updated_trip.cautions
        assert caution2 in updated_trip.cautions

    def test_update_baggage_summary(self):
        """수화물 요약 업데이트."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        summary = [{"category": "clothing", "count": 5}]
        updated_trip = trip.update_baggage_summary(summary)

        assert updated_trip.baggage_summary == summary
        assert updated_trip is not trip

    def test_bagggage_summary_is_list_of_dicts(self):
        """baggage_summary가 list[dict] 타입."""
        trip = Trip.create(
            title="도쿄 여행",
            destination="일본 도쿄",
            purpose=["쇼핑"],
            user_id="user-123",
        )

        summary = [{"category": "clothing", "count": 5}]
        updated_trip = trip.update_baggage_summary(summary)

        assert isinstance(updated_trip.baggage_summary, list)
        assert all(isinstance(item, dict) for item in updated_trip.baggage_summary)