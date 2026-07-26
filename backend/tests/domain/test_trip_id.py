"""TripId Value Object 단위 테스트."""

import pytest
from uuid import uuid4

from app.domain.value_objects.trip_id import TripId


class TestTripId:
    """TripId 값 객체 테스트."""

    def test_from_string_creates_trip_id(self):
        """문자열로부터 TripId 생성."""
        uuid_value = uuid4()
        trip_id = TripId.from_string(str(uuid_value))

        assert trip_id.value == uuid_value

    def test_str_returns_string_representation(self):
        """문자열로 변환."""
        uuid_value = uuid4()
        trip_id = TripId(uuid_value)

        assert str(trip_id) == str(uuid_value)

    def test_from_string_with_invalid_uuid_raises_error(self):
        """유효하지 않은 UUID 문자열로 TripId 생성 시 에러."""
        with pytest.raises(ValueError):
            TripId.from_string("invalid-uuid")

    def test_frozen_prevents_mutation(self):
        """불변성 확인."""
        uuid_value = uuid4()
        trip_id = TripId(uuid_value)

        with pytest.raises(AttributeError):
            trip_id.value = uuid4()

    def test_value_object_equality(self):
        """값 객체 동등성 확인."""
        uuid_value = uuid4()
        trip_id1 = TripId(uuid_value)
        trip_id2 = TripId(uuid_value)

        assert trip_id1 == trip_id2

    def test_value_object_inequality(self):
        """값 객체 비동등성 확인."""
        trip_id1 = TripId(uuid4())
        trip_id2 = TripId(uuid4())

        assert trip_id1 != trip_id2