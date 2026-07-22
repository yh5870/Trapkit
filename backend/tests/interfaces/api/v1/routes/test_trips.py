"""Streaming API tests."""

import json
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.application.commands.create_trip import CreateTripCommand
from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from app.main import app
from infrastructure.external.gemini_client import GeminiClient


@pytest.fixture
def client() -> TestClient:
    """테스트용 FastAPI 클라이언트."""
    return TestClient(app)


@pytest.fixture
def mock_trip() -> Trip:
    """테스트용 Trip."""
    return Trip.create(
        title="제주도 여행",
        destination="제주도",
        purpose=["관광", "맛집 투어"],
        user_id="test-user",
        duration_nights=3,
        departure_month=8,
        companions="가족",
        cautions=[{"type": "weather", "message": "비 우산 챙기기"}],
        baggage_summary=[{"category": "clothing", "count": 5}],
    )


@pytest.fixture
def mock_ai_content() -> dict:
    """테스트용 AI 콘텐츠."""
    return {
        "cautions": [
            {"type": "weather", "message": "비 우산 챙기기"},
            {"type": "health", "message": "여행자 보험 가입"},
        ],
        "baggage_summary": [
            {"category": "clothing", "count": 5},
            {"category": "electronics", "count": 3},
        ],
    }


class TestStreamTripGeneration:
    """_stream_trip_generation 함수 테스트."""

    @pytest.mark.asyncio
    async def test_stream_trip_generation_success(
        self, mock_trip: Trip, mock_ai_content: dict
    ) -> None:
        """스트리밍 성공 테스트."""
        # Given
        command = CreateTripCommand(
            user_id="test-user",
            destination="제주도",
            purpose=["관광"],
            duration_nights=3,
            departure_month=8,
            companions="가족",
        )

        from interfaces.api.v1.routes.trips import _stream_trip_generation

        mock_repo = MagicMock()
        mock_repo.save = AsyncMock(return_value=mock_trip)

        mock_client = MagicMock()
        mock_client.generate_trip_content = AsyncMock(return_value=mock_ai_content)

        # When
        events = []
        async for event in _stream_trip_generation(command, mock_repo, mock_client):
            events.append(event)

        # Then
        assert len(events) > 0

        # 이벤트 타입 확인
        event_types = []
        for event in events:
            if "event: started" in event:
                event_types.append("started")
            elif "event: generating" in event:
                event_types.append("generating")
            elif "event: content" in event:
                event_types.append("content")
            elif "event: creating" in event:
                event_types.append("creating")
            elif "event: saving" in event:
                event_types.append("saving")
            elif "event: completed" in event:
                event_types.append("completed")

        assert "started" in event_types
        assert "generating" in event_types
        assert "content" in event_types
        assert "creating" in event_types
        assert "saving" in event_types
        assert "completed" in event_types

    @pytest.mark.asyncio
    async def test_stream_trip_generation_error(
        self,
    ) -> None:
        """스트리밍 에러 테스트."""
        # Given
        command = CreateTripCommand(
            user_id="test-user",
            destination="제주도",
            purpose=["관광"],
        )

        from interfaces.api.v1.routes.trips import _stream_trip_generation

        mock_repo = MagicMock()
        mock_repo.save = AsyncMock(side_effect=Exception("DB 오류"))

        mock_client = MagicMock()
        mock_client.generate_trip_content = AsyncMock(return_value={"cautions": [], "baggage_summary": []})

        # When & Then
        events = []
        async for event in _stream_trip_generation(command, mock_repo, mock_client):
            events.append(event)

        # 에러 이벤트 확인
        assert any("event: error" in event for event in events)


class TestGenerateTripStream:
    """generate_trip_stream 엔드포인트 테스트."""

    @pytest.mark.asyncio
    async def test_generate_trip_stream_success(self, client: TestClient) -> None:
        """성공적인 스트리밍 요청 테스트."""
        # Given
        mock_ai_content = {
            "cautions": [{"type": "weather", "message": "비 우산 챙기기"}],
            "baggage_summary": [{"category": "clothing", "count": 5}],
        }

        mock_saved_trip = Trip.create(
            title="제주도 여행",
            destination="제주도",
            purpose=["관광"],
            user_id="test-user",
            cautions=mock_ai_content["cautions"],
            baggage_summary=mock_ai_content["baggage_summary"],
        )

        with patch("infrastructure.database.dependencies.get_trip_repository") as mock_get_repo:
            mock_repo = MagicMock()
            mock_repo.save = AsyncMock(return_value=mock_saved_trip)
            mock_get_repo.return_value = mock_repo

            with patch("infrastructure.external.gemini_client.GeminiClient") as mock_client_class:
                mock_client = MagicMock()
                mock_client.generate_trip_content = AsyncMock(return_value=mock_ai_content)
                mock_client_class.return_value = mock_client

                # When
                response = client.post(
                    "/api/v1/trips/generate",
                    params={
                        "user_id": "test-user",
                        "destination": "제주도",
                        "purpose": ["관광"],
                        "duration_nights": 3,
                        "departure_month": 8,
                        "companions": "가족",
                    },
                )

                # Then
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
                assert "Cache-Control" in response.headers
                assert "no-cache" in response.headers["Cache-Control"]


class TestFormatSSEEvent:
    """_format_sse_event 함수 테스트."""

    def test_format_sse_event_message(self) -> None:
        """message 이벤트 포맷팅 테스트."""
        # Given
        data = {"status": "started", "message": "시작"}

        # When
        from interfaces.api.v1.routes.trips import _format_sse_event
        result = _format_sse_event(data, "message")

        # Then
        assert "event: message" in result
        assert "data: " in result
        assert '"status": "started"' in result
        assert '"message": "시작"' in result
        assert result.endswith("\n\n")

    def test_format_sse_event_error(self) -> None:
        """error 이벤트 포맷팅 테스트."""
        # Given
        data = {"status": "error", "message": "에러 발생"}

        # When
        from interfaces.api.v1.routes.trips import _format_sse_event
        result = _format_sse_event(data, "error")

        # Then
        assert "event: error" in result
        assert '"status": "error"' in result
        assert '"message": "에러 발생"' in result

    def test_format_sse_event_korean(self) -> None:
        """한글 포맷팅 테스트."""
        # Given
        data = {"destination": "제주도", "purpose": ["관광", "맛집 투어"]}

        # When
        from interfaces.api.v1.routes.trips import _format_sse_event
        result = _format_sse_event(data, "content")

        # Then
        assert "제주도" in result
        assert "관광" in result
        assert "맛집 투어" in result