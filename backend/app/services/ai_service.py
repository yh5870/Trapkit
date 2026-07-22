"""AI 호출 서비스 (Google Gemini)."""

import google.generativeai as genai

from app.config import settings
from app.schemas.ai import AITripResponse


class AIService:
    """AI 서비스."""

    def __init__(self) -> None:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    async def generate_trip_list(self, prompt: dict) -> AITripResponse:
        """AI 리스트 생성."""
        # TODO: 실제 AI 호출 구현
        # response = self.model.generate_content(
        #     self._get_user_prompt(prompt),
        #     generation_config=genai.types.GenerationConfig(
        #         max_output_tokens=settings.AI_MAX_TOKENS,
        #         temperature=0.7,
        #     ),
        #     system_instruction=self._get_system_prompt(),
        # )
        # return self._parse_response(response)

        # 임시 응답
        return AITripResponse(
            trip_title="임시 트립 제목",
            categories=[],
            cautions=[],
            baggage_summary=[],
        )

    def _get_system_prompt(self) -> str:
        """시스템 프롬프트."""
        return """너는 여행 준비물 전문가다. 여행 정보를 바탕으로 준비물 체크리스트,
여행지 주의사항, 수화물 규정 요약을 JSON으로만 응답한다.
- 마크다운, 설명 문장 없이 JSON만 출력한다.
- 목적지의 기후(출발 월 기준), 전압/플러그, 관습을 반드시 반영한다.
- 여행 목적에 특화된 항목을 반드시 포함한다.
- 수화물 규정 요약에는 생성한 준비물 중 규정 이슈가 있는 항목만 담는다.
- 확실하지 않은 시의성 정보(비자 등)는 confidence: "check_required"로 표시한다."""

    def _get_user_prompt(self, prompt: dict) -> str:
        """사용자 프롬프트."""
        return f"""
다음 여행 정보를 바탕으로 준비물 체크리스트를 JSON으로만 출력하라:
- 목적지: {prompt.get('destination')}
- 목적: {prompt.get('purpose', [])}
- 기간: {prompt.get('duration_nights')}박
- 출발 월: {prompt.get('departure_month')}월
- 동행: {prompt.get('companions')}
"""

    def _parse_response(self, response) -> AITripResponse:
        """AI 응답 파싱."""
        # TODO: JSON 파싱 및 스키마 검증
        pass


# 싱글톤 인스턴스
ai_service = AIService()