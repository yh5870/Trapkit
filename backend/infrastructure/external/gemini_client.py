"""Gemini AI Client.

Google Gemini API를 통한 트립 콘텐츠 생성.
AIClient 인터페이스를 구현하여 도메인 서비스와 AI 인프라를 분리.
"""

import asyncio
import hashlib
import json
import logging
from typing import Any

from google import genai
from google.genai import types
from google.genai.errors import ClientError

from app.application.commands.create_trip import CreateTripCommand
from app.core.redis import cache_get, cache_set
from app.domain.services.trip_generation_service import AIClient
from app.config import settings

logger = logging.getLogger(__name__)


class GeminiClient(AIClient):
    """Google Gemini AI 클라이언트 (google.genai 사용)."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """초기화.

        Args:
            api_key: Gemini API 키 (기본값: settings.GEMINI_API_KEY)
            model: Gemini 모델명 (기본값: settings.GEMINI_MODEL)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL

        # Gemini 클라이언트 초기화 (새 API)
        self.client = genai.Client(api_key=self.api_key)
        self.max_retries = 3
        self.initial_backoff = 40  # seconds

    async def _generate_with_retry(self, prompt: str) -> Any:
        """AI 생성 요청을 지수 백오프로 재시도.

        Args:
            prompt: 프롬프트

        Returns:
            AI 응답

        Raises:
            ClientError: 모든 재시도 실패 시
        """
        backoff = self.initial_backoff

        for attempt in range(self.max_retries):
            try:
                return await self.client.aio.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=settings.AI_MAX_TOKENS,
                        temperature=0.7,
                    ),
                )
            except ClientError as e:
                if e.code == 429:
                    # 할당량 초과 - 재시도 무의미하므로 즉시 에러 반환
                    logger.error("Gemini API quota exceeded (할당량 초과)")
                    raise ClientError(
                        429,
                        {"error": {"message": "API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요."}}
                    )
                else:
                    # 기타 에러 - 재시도
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"Gemini API error (attempt {attempt + 1}/{self.max_retries}): {e}. Retrying in {backoff}s..."
                        )
                        await asyncio.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Gemini API error after {self.max_retries} attempts: {e}")
                        raise

        raise ClientError(429, {"error": {"message": "Max retries exceeded for quota limit"}})

    async def generate_trip_content(self, command: CreateTripCommand) -> dict[str, Any]:
        """AI를 통해 트립 콘텐츠 생성.

        캐싱을 통해 비용 절감.

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

        # 3. AI 생성 (새 API 사용, 재시도 로직 포함)
        response = await self._generate_with_retry(prompt)

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
        prompt = f"""여행 '{command.destination}'에 대한 주의사항과 체크리스트를 생성해주세요.

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
        {"type": "weather|health|safety|other", "message": "주의사항 내용"}
    ],
    "items": [
        {
            "category": "카테고리명 (예: 옷, 전자기기, 필수품)",
            "name": "아이템명",
            "quantity": 수량 (기본 1)",
            "tip": "팁 (선택적, null 또는 팁 내용)",
            "baggage_flag": true/false
        }
    ]
}

카테고리 예시: 옷, 전자기기, 필수품, 화장품, 위생용품, 약품, 문서, 기타
아이템은 총 15-20개로, 여행지와 목적에 맞는 실용적인 것들만 선택해주세요.
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

        # items가 없으면 빈 리스트
        if "items" not in content:
            content["items"] = []

        # 호환성: baggage_summary가 없으면 items로부터 생성
        if "baggage_summary" not in content and content.get("items"):
            # items에서 카테고리별 카운트 계산
            category_counts: dict[str, int] = {}
            for item in content["items"]:
                category = item.get("category", "기타")
                category_counts[category] = category_counts.get(category, 0) + 1

            content["baggage_summary"] = [
                {"category": cat, "count": count}
                for cat, count in category_counts.items()
            ]

        return content