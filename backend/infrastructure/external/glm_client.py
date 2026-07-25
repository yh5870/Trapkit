"""GLM AI Client (ZhipuAI).

智谱AI GLM API를 통한 트립 콘텐츠 생성.
AIClient 인터페이스를 구현하여 도메인 서비스와 AI 인프라를 분리.
"""

import asyncio
import hashlib
import json
import logging
from typing import Any

from zhipuai import ZhipuAI
from app.application.commands.create_trip import CreateTripCommand
from app.core.redis import cache_get, cache_set
from app.domain.services.trip_generation_service import AIClient
from app.config import settings

logger = logging.getLogger(__name__)


class GLMClient(AIClient):
    """ZhipuAI GLM AI 클라이언트."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        """초기화.

        Args:
            api_key: GLM API 키 (기본값: settings.GLM_API_KEY)
            model: GLM 모델명 (기본값: settings.GLM_MODEL)
        """
        self.api_key = api_key or settings.GLM_API_KEY
        self.model = model or settings.GLM_MODEL

        # GLM 클라이언트 초기화 (ZhipuAI)
        self.client = ZhipuAI(api_key=self.api_key)
        self.max_retries = 3
        self.initial_backoff = 10  # seconds (GLM은 빠름)

    async def _generate_with_retry(self, prompt: str) -> Any:
        """AI 생성 요청을 지수 백오프로 재시도.

        Args:
            prompt: 프롬프트

        Returns:
            AI 응답

        Raises:
            Exception: 모든 재시도 실패 시
        """
        backoff = self.initial_backoff

        for attempt in range(self.max_retries):
            try:
                # GLM API는 동기 API이므로 run_in_executor 사용
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a helpful travel assistant."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=settings.AI_MAX_TOKENS,
                        temperature=0.7,
                    )
                )
                return response
            except Exception as e:
                # GLM API 에러 처리
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "rate limit" in error_str.lower():
                    # 할당량 초과 - 재시도 무의미하므로 즉시 에러 반환
                    logger.error(f"GLM API quota exceeded: {e}")
                    raise Exception("API 할당량이 초과되었습니다. 잠시 후 다시 시도해주세요.") from e
                else:
                    # 기타 에러 - 재시도
                    if attempt < self.max_retries - 1:
                        logger.warning(
                            f"GLM API error (attempt {attempt + 1}/{self.max_retries}): {e}. "
                            f"Retrying in {backoff}s..."
                        )
                        await asyncio.sleep(backoff)
                        backoff *= 2  # Exponential backoff
                        continue
                    else:
                        logger.error(f"GLM API error after {self.max_retries} attempts: {e}")
                        raise

        raise Exception("GLM API 호출 실패")

    async def generate_trip_content(self, command: CreateTripCommand) -> dict[str, Any]:
        """AI를 통해 트립 콘텐츠 생성.

        캐싱을 통해 비용 절감.

        Args:
            command: Trip 생성 Command

        Returns:
            AI 생성 콘텐츠:
                - cautions: 주의사항 리스트 (category / text / confidence)
                - items: 체크리스트 아이템 리스트 (baggage_flag 정규화 완료)
                - baggage_summary: 수화물 규정 확인이 필요한 카테고리별 건수

        Example:
            >>> content = await client.generate_trip_content(command)
            >>> content
            {
                "cautions": [
                    {"category": "weather", "text": "비 우산 챙기기", "confidence": "stable"}
                ],
                "items": [
                    {
                        "category": "전자기기",
                        "name": "보조배터리",
                        "quantity": "1개",
                        "tip": "100Wh 이하만 가능",
                        "baggage_flag": "carry_on_only"
                    }
                ],
                "baggage_summary": [
                    {"category": "전자기기", "count": 1}
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
        response = await self._generate_with_retry(prompt)

        # 4. 결과 파싱
        content_text = response.choices[0].message.content
        content = self._parse_response(content_text)

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
        return f"trip:glm:{hashlib.md5(command_str.encode()).hexdigest()}"

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
        {"category": "weather|health|safety|other", "text": "주의사항 내용", "confidence": "stable|check_required"}
    ],
    "items": [
        {
            "category": "카테고리명 (예: 옷, 전자기기, 필수품)",
            "name": "아이템명",
            "quantity": "수량 문자열 (예: \\"1개\\", \\"2벌\\", 기본 \\"1개\\")",
            "tip": "팁 (선택적, null 또는 팁 내용)",
            "baggage_flag": "carry_on_only | checked_only | restricted | null"
        }
    ]
}

카테고리 예시: 옷, 전자기기, 필수품, 화장품, 위생용품, 약품, 문서, 기타

baggage_flag 규칙 (매우 중요):
- 반드시 아래 4개 값 중 하나의 **문자열**이어야 합니다. true/false 같은 불리언은 절대 사용하지 마세요.
- "carry_on_only": 기내 반입만 가능 (예: 보조배터리, 리튬 배터리, 전자담배)
- "checked_only": 위탁 수하물만 가능 (예: 100ml 초과 액체, 칼, 스프레이)
- "restricted": 수량/용량 제한이 있음 (예: 100ml 이하 화장품, 의약품)
- null: 수화물 규정과 무관한 일반 물품 (대부분의 아이템이 여기 해당)

quantity는 반드시 문자열로 작성하세요 (숫자가 아님).
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

        # cautions 필드명 정규화 (구형 type/message 응답 대응)
        normalized_cautions = []
        for c in content["cautions"]:
            normalized_cautions.append({
                "category": c.get("category", c.get("type", "other")),
                "text": c.get("text", c.get("message", "")),
                "confidence": c.get("confidence", "stable"),
            })
        content["cautions"] = normalized_cautions

        # items가 없으면 빈 리스트
        if "items" not in content:
            content["items"] = []

        # items 필드 정규화 (baggage_flag 불리언 응답 대응)
        normalized_items = []
        for i in content["items"]:
            if not isinstance(i, dict):
                continue

            quantity = i.get("quantity")
            normalized_items.append({
                "category": i.get("category") or "기타",
                "name": i.get("name") or "아이템",
                # quantity가 숫자로 와도 문자열로 통일 (스키마: str | None)
                "quantity": str(quantity) if quantity is not None else None,
                "tip": i.get("tip"),
                "baggage_flag": self._normalize_baggage_flag(i.get("baggage_flag")),
            })
        content["items"] = normalized_items

        # 호환성: baggage_summary가 없으면 items로부터 생성
        # 주의: '수화물 규정 확인 필요' 건수이므로 baggage_flag가 있는 아이템만 집계한다.
        if "baggage_summary" not in content and content.get("items"):
            category_counts: dict[str, int] = {}
            for item in content["items"]:
                if not item.get("baggage_flag"):
                    continue
                category = item.get("category", "기타")
                category_counts[category] = category_counts.get(category, 0) + 1

            content["baggage_summary"] = [
                {"category": cat, "count": count}
                for cat, count in category_counts.items()
            ]

        return content

    @staticmethod
    def _normalize_baggage_flag(raw: Any) -> str | None:
        """baggage_flag를 도메인이 기대하는 문자열 리터럴로 정규화.

        AI가 불리언(true/false)이나 예상 밖의 값을 반환해도
        'carry_on_only' | 'checked_only' | 'restricted' | None 으로 수렴시킨다.

        Args:
            raw: AI 응답의 baggage_flag 원본 값

        Returns:
            정규화된 flag 문자열, 규정과 무관하면 None
        """
        VALID = {"carry_on_only", "checked_only", "restricted"}

        if raw is None:
            return None

        # 불리언 응답: True는 '규정 있음'이라는 정보만 있으므로 restricted로 격하
        if isinstance(raw, bool):
            return "restricted" if raw else None

        if isinstance(raw, str):
            value = raw.strip().lower()
            if value in VALID:
                return value
            # 문자열로 온 불리언 ("true" / "false" / "False" 등) 방어
            if value in {"false", "none", "null", ""}:
                return None
            if value == "true":
                return "restricted"

        return None