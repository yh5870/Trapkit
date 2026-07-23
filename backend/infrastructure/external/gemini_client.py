"""Gemini AI Client.

Google Gemini API를 통한 트립 콘텐츠 생성.
AIClient 인터페이스를 구현하여 도메인 서비스와 AI 인프라를 분리.
"""

import hashlib
import json
from typing import Any

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from app.application.commands.create_trip import CreateTripCommand
from app.core.redis import cache_get, cache_set
from app.domain.services.trip_generation_service import AIClient
from app.config import settings


class GeminiClient(AIClient):
    """Google Gemini AI 클라이언트."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """초기화.

        Args:
            api_key: Gemini API 키 (기본값: settings.GEMINI_API_KEY)
            model: Gemini 모델명 (기본값: settings.GEMINI_MODEL)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

        # Gemini 초기화
        genai.configure(api_key=self.api_key)
        self.client = genai.GenerativeModel(self.model)

    async def generate_trip_content(self, command: CreateTripCommand) -> dict[str, Any]:
        """AI를 통해 트립 콘텐츠 생성.

        캐싱을 통해 비용 절감.
        스트리밍 지원으로 실시간 응답 가능.

        Args:
            command: Trip 생성 Command

        Returns:
            AI 생성 콘텐츠:
                - cautions: 주의사항 리스트
                - baggage_summary: 수화물 요약 리스트

        Example:
            >>> content = await client.generate_trip_content(command)
            >>> content
            {
                "cautions": [
                    {"type": "weather", "message": "비 우산 챙기기"}
                ],
                "baggage_summary": [
                    {"category": "clothing", "count": 5}
                ]
            }
        """
        # 1. 캐시 확인
        cache_key = self._get_cache_key(command)
        cached = await cache_get(cache_key)

        if cached:
            try:
                return json.loads(cached)
            except json.JSONDecodeError:
                # 캐시 손상 시 재생성
                pass

        # 2. 프롬프트 빌드
        prompt = self._build_prompt(command)

        # 3. AI 생성
        generation_config = GenerationConfig(
            max_output_tokens=settings.AI_MAX_TOKENS,
            temperature=0.7,
        )

        response = await self.client.generate_content_async(
            prompt,
            generation_config=generation_config,
        )

        # 4. 결과 파싱
        content = self._parse_response(response.text)

        # 5. 캐시 저장 (24시간 TTL)
        await cache_set(cache_key, json.dumps(content), ttl=settings.AI_CACHE_TTL)

        return content

    def _get_cache_key(self, command: CreateTripCommand) -> str:
        """캐시 키 생성.

        Command 해시를 통해 캐시 키 생성.

        Args:
            command: Trip 생성 Command

        Returns:
            캐시 키
        """
        # Command 직렬화
        command_data = {
            "destination": command.destination,
            "purpose": command.purpose,
            "duration_nights": command.duration_nights,
            "departure_month": command.departure_month,
            "companions": command.companions,
        }

        # 해시 생성
        command_str = json.dumps(command_data, sort_keys=True)
        return f"trip:{hashlib.md5(command_str.encode()).hexdigest()}"

    def _build_prompt(self, command: CreateTripCommand) -> str:
        """프롬프트 빌드.

        AI가 이해하기 쉬운 프롬프트 생성.

        Args:
            command: Trip 생성 Command

        Returns:
            프롬프트 문자열
        """
        # 기본 프롬프트
        prompt = f"""여행 '{command.destination}'에 대한 주의사항과 수화물 리스트를 생성해주세요.

여행 목적: {', '.join(command.purpose)}"""

        # 선택적 정보 추가
        if command.duration_nights:
            prompt += f"\n여행 기간: {command.duration_nights}박"

        if command.departure_month:
            prompt += f"\n출발 월: {command.departure_month}월"

        if command.companions:
            prompt += f"\n동행인: {command.companions}"

        # 응답 형식 지정
        prompt += """

다음 JSON 형식으로 응답해주세요:
{
    "cautions": [
        {"type": "weather|weather|health|safety|other", "message": "주의사항 내용"}
    ],
    "baggage_summary": [
        {"category": "clothing|electronics|documents|other", "count": 개수}
    ]
}

주의사항은 최대 5개, 수화물 카테고리는 최대 10개로 해주세요.
JSON만 응답해주세요. 다른 텍스트는 포함하지 마세요."""

        return prompt

    def _parse_response(self, response_text: str) -> dict[str, Any]:
        """AI 응답 파싱.

        Args:
            response_text: AI 응답 텍스트

        Returns:
            파싱된 콘텐츠

        Raises:
            ValueError: JSON 파싱 실패 시
        """
        # JSON 부분 추출 (마크다운 코드 블록 제거)
        text = response_text.strip()

        # ```json ... ``` 형식 제거
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        # JSON 파싱
        try:
            content = json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"AI 응답 JSON 파싱 실패: {e}") from e

        # 필수 필드 확인
        if "cautions" not in content:
            content["cautions"] = []

        if "baggage_summary" not in content:
            content["baggage_summary"] = []

        return content