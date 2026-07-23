"""GeminiClient tests."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.commands.create_trip import CreateTripCommand
from app.config import settings
from infrastructure.external.gemini_client import GeminiClient


@pytest.fixture
def mock_command() -> CreateTripCommand:
    """테스트용 CreateTripCommand."""
    return CreateTripCommand(
        user_id="test-user",
        destination="제주도",
        purpose=["관광", "맛집 투어"],
        duration_nights=3,
        departure_month=8,
        companions="가족",
    )


@pytest.fixture
def mock_response_text() -> str:
    """테스트용 AI 응답."""
    return """{
    "cautions": [
        {"type": "weather", "message": "비 우산 챙기기"},
        {"type": "health", "message": "여행자 보험 가입"}
    ],
    "baggage_summary": [
        {"category": "clothing", "count": 5},
        {"category": "electronics", "count": 3}
    ]
}"""


@pytest.fixture
def client() -> GeminiClient:
    """테스트용 GeminiClient."""
    return GeminiClient(api_key="test-api-key", model="test-model")


class TestGeminiClient:
    """GeminiClient 테스트."""

    @pytest.mark.asyncio
    async def test_generate_trip_content_success(
        self, client: GeminiClient, mock_command: CreateTripCommand, mock_response_text: str
    ) -> None:
        """generate_trip_content() 성공 테스트."""
        # Given
        mock_response = MagicMock()
        mock_response.text = mock_response_text

        with patch.object(client.client, "generate_content_async", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            with patch("infrastructure.external.gemini_client.cache_get", new_callable=AsyncMock) as mock_cache_get:
                mock_cache_get.return_value = None

                with patch("infrastructure.external.gemini_client.cache_set", new_callable=AsyncMock) as mock_cache_set:
                    # When
                    result = await client.generate_trip_content(mock_command)

                    # Then
                    assert "cautions" in result
                    assert "baggage_summary" in result
                    assert len(result["cautions"]) == 2
                    assert len(result["baggage_summary"]) == 2
                    assert result["cautions"][0]["type"] == "weather"
                    assert result["baggage_summary"][0]["category"] == "clothing"

                    # 캐시 저장 호출 확인
                    mock_cache_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_trip_content_cache_hit(
        self, client: GeminiClient, mock_command: CreateTripCommand, mock_response_text: str
    ) -> None:
        """캐시 적중 테스트."""
        # Given
        cached_data = json.dumps({
            "cautions": [{"type": "test", "message": "cached"}],
            "baggage_summary": [{"category": "test", "count": 1}]
        })

        with patch("infrastructure.external.gemini_client.cache_get", new_callable=AsyncMock) as mock_cache_get:
            mock_cache_get.return_value = cached_data

            with patch.object(client.client, "generate_content_async", new_callable=AsyncMock) as mock_generate:
                # When
                result = await client.generate_trip_content(mock_command)

                # Then
                assert result["cautions"][0]["message"] == "cached"

                # AI 호출 안 함 (캐시 적중)
                mock_generate.assert_not_called()

    @pytest.mark.asyncio
    async def test_generate_trip_content_with_markdown(
        self, client: GeminiClient, mock_command: CreateTripCommand
    ) -> None:
        """마크다운 코드 블록 제거 테스트."""
        # Given
        markdown_response = """```json
{
    "cautions": [{"type": "test", "message": "test"}],
    "baggage_summary": [{"category": "test", "count": 1}]
}
```"""

        mock_response = MagicMock()
        mock_response.text = markdown_response

        with patch.object(client.client, "generate_content_async", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            with patch("infrastructure.external.gemini_client.cache_get", new_callable=AsyncMock) as mock_cache_get:
                mock_cache_get.return_value = None

                # When
                result = await client.generate_trip_content(mock_command)

                # Then
                assert "cautions" in result
                assert "baggage_summary" in result

    @pytest.mark.asyncio
    async def test_generate_trip_content_parse_error(
        self, client: GeminiClient, mock_command: CreateTripCommand
    ) -> None:
        """JSON 파싱 실패 테스트."""
        # Given
        invalid_json = "This is not JSON"

        mock_response = MagicMock()
        mock_response.text = invalid_json

        with patch.object(client.client, "generate_content_async", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            with patch("infrastructure.external.gemini_client.cache_get", new_callable=AsyncMock) as mock_cache_get:
                mock_cache_get.return_value = None

                # When & Then
                with pytest.raises(ValueError, match="JSON 파싱 실패"):
                    await client.generate_trip_content(mock_command)

    @pytest.mark.asyncio
    async def test_generate_trip_content_missing_fields(
        self, client: GeminiClient, mock_command: CreateTripCommand
    ) -> None:
        """필드 누락 시 기본값 테스트."""
        # Given
        partial_json = '{"other": "data"}'

        mock_response = MagicMock()
        mock_response.text = partial_json

        with patch.object(client.client, "generate_content_async", new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = mock_response

            with patch("infrastructure.external.gemini_client.cache_get", new_callable=AsyncMock) as mock_cache_get:
                mock_cache_get.return_value = None

                # When
                result = await client.generate_trip_content(mock_command)

                # Then
                assert "cautions" in result
                assert "baggage_summary" in result
                assert result["cautions"] == []
                assert result["baggage_summary"] == []

    def test_get_cache_key(self, client: GeminiClient, mock_command: CreateTripCommand) -> None:
        """캐시 키 생성 테스트."""
        # When
        key = client._get_cache_key(mock_command)

        # Then
        assert key.startswith("trip:")
        # 동일 커맨드는 동일 키
        key2 = client._get_cache_key(mock_command)
        assert key == key2

        # 다른 커맨드는 다른 키
        different_command = CreateTripCommand(
            user_id="test-user",
            destination="도쿄",
            purpose=["쇼핑"],
        )
        different_key = client._get_cache_key(different_command)
        assert key != different_key

    def test_build_prompt(self, client: GeminiClient, mock_command: CreateTripCommand) -> None:
        """프롬프트 빌드 테스트."""
        # When
        prompt = client._build_prompt(mock_command)

        # Then
        assert "제주도" in prompt
        assert "관광, 맛집 투어" in prompt
        assert "3박" in prompt
        assert "8월" in prompt
        assert "가족" in prompt
        assert "JSON 형식" in prompt
        assert "cautions" in prompt
        assert "baggage_summary" in prompt

    def test_build_prompt_minimal(self, client: GeminiClient) -> None:
        """최소 정보 프롬프트 테스트."""
        # Given
        minimal_command = CreateTripCommand(
            user_id="test-user",
            destination="부산",
            purpose=["해수욕"],
        )

        # When
        prompt = client._build_prompt(minimal_command)

        # Then
        assert "부산" in prompt
        assert "해수욕" in prompt
        assert "여행 기간" not in prompt
        assert "출발 월" not in prompt
        assert "동행인" not in prompt

    def test_parse_response(self, client: GeminiClient) -> None:
        """응답 파싱 테스트."""
        # Given
        json_text = """{
    "cautions": [
        {"type": "weather", "message": "비 우산 챙기기"}
    ],
    "baggage_summary": [
        {"category": "clothing", "count": 5}
    ]
}"""

        # When
        result = client._parse_response(json_text)

        # Then
        assert result["cautions"][0]["message"] == "비 우산 챙기기"
        assert result["baggage_summary"][0]["category"] == "clothing"

    def test_parse_response_with_markdown(self, client: GeminiClient) -> None:
        """마크다운 코드 블록 제거 테스트."""
        # Given
        markdown_json = """```json
{
    "cautions": [],
    "baggage_summary": []
}
```"""

        # When
        result = client._parse_response(markdown_json)

        # Then
        assert result["cautions"] == []
        assert result["baggage_summary"] == []

    def test_parse_response_invalid_json(self, client: GeminiClient) -> None:
        """잘못된 JSON 테스트."""
        # Given
        invalid_json = "not json"

        # When & Then
        with pytest.raises(ValueError, match="JSON 파싱 실패"):
            client._parse_response(invalid_json)