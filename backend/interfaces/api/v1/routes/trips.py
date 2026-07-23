"""Trip 스트리밍 API 라우터.

AI를 통한 트립 생성 스트리밍 엔드포인트.
Server-Sent Events (SSE)를 사용하여 실시간으로 AI 응답 전송.
"""

import json
from datetime import datetime
from typing import Any, AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.application.commands.create_trip import CreateTripCommand
from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository
from app.domain.services.trip_generation_service import TripGenerationService
from app.domain.value_objects.trip_id import TripId
from app.utils.logger import setup_logger
from infrastructure.database.dependencies import get_trip_repository
from infrastructure.external.gemini_client import GeminiClient
from shared.config.database import get_db

logger = setup_logger(__name__)
router = APIRouter()


# 스트리밍 응답을 위한 JSON 형식
def _format_sse_event(data: dict[str, Any], event_type: str = "message") -> str:
    """Server-Sent Events 이벤트 포맷팅.

    Args:
        data: 이벤트 데이터
        event_type: 이벤트 타입 (message, error, done)

    Returns:
        SSE 포맷 문자열
    """
    event_str = f"event: {event_type}\n"
    data_str = json.dumps(data, ensure_ascii=False, default=str)
    event_str += f"data: {data_str}\n\n"
    return event_str


async def _stream_trip_generation(
    command: CreateTripCommand,
    trip_repo: TripRepository,
    ai_client: GeminiClient,
) -> AsyncGenerator[str, None]:
    """트립 생성 스트리밍 함수.

    AI 응답을 실시간으로 전송하고 최종적으로 Trip 객체를 전송.

    Args:
        command: Trip 생성 Command
        trip_repo: Trip Repository
        ai_client: AI Client

    Yields:
        SSE 포맷 스트리밍 데이터

    Example:
        >>> async for chunk in _stream_trip_generation(command, repo, client):
        ...     yield chunk
    """
    try:
        # 1. 시작 알림
        yield _format_sse_event(
            {
                "status": "started",
                "message": "트립 생성을 시작합니다...",
                "destination": command.destination,
            },
            event_type="started",
        )

        # 2. AI 콘텐츠 생성
        yield _format_sse_event(
            {
                "status": "generating",
                "message": "AI로부터 콘텐츠를 생성 중입니다...",
            },
            event_type="generating",
        )

        ai_content = await ai_client.generate_trip_content(command)

        # 3. AI 콘텐츠 전송
        yield _format_sse_event(
            {
                "status": "content_generated",
                "content": ai_content,
            },
            event_type="content",
        )

        # 4. Trip 엔티티 생성
        yield _format_sse_event(
            {
                "status": "creating_entity",
                "message": "Trip 엔티티를 생성 중입니다...",
            },
            event_type="creating",
        )

        trip = Trip.create(
            title=command.destination,
            destination=command.destination,
            purpose=command.purpose,
            user_id=command.user_id,
            duration_nights=command.duration_nights,
            departure_month=command.departure_month,
            companions=command.companions,
            cautions=ai_content.get("cautions", []),
            baggage_summary=ai_content.get("baggage_summary", []),
        )

        # 5. 저장
        yield _format_sse_event(
            {
                "status": "saving",
                "message": "데이터베이스에 저장 중입니다...",
            },
            event_type="saving",
        )

        saved_trip = await trip_repo.save(trip)

        # 6. 완료 - 최종 Trip 객체 전송
        yield _format_sse_event(
            {
                "status": "completed",
                "trip": {
                    "id": str(saved_trip.id.value),
                    "title": saved_trip.title,
                    "destination": saved_trip.destination,
                    "purpose": saved_trip.purpose,
                    "user_id": saved_trip.user_id,
                    "duration_nights": saved_trip.duration_nights,
                    "departure_month": saved_trip.departure_month,
                    "companions": saved_trip.companions,
                    "cautions": saved_trip.cautions,
                    "baggage_summary": saved_trip.baggage_summary,
                    "created_at": saved_trip.created_at.isoformat(),
                    "updated_at": saved_trip.updated_at.isoformat(),
                },
            },
            event_type="completed",
        )

    except Exception as e:
        logger.error(f"트립 생성 스트리밍 실패: {e}")
        yield _format_sse_event(
            {
                "status": "error",
                "message": f"트립 생성 중 오류가 발생했습니다: {str(e)}",
            },
            event_type="error",
        )
        raise


@router.post("/generate")
async def generate_trip_stream(
    user_id: str,
    destination: str,
    purpose: list[str],
    duration_nights: int | None = None,
    departure_month: int | None = None,
    companions: str | None = None,
    trip_repo: TripRepository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """AI를 통한 트립 생성 스트리밍.

    Server-Sent Events (SSE)를 사용하여 실시간으로 AI 응답 전송.

    Args:
        user_id: 사용자 ID (인증 토큰에서 추출)
        destination: 여행지
        purpose: 여행 목적 리스트
        duration_nights: 여행 기간 (박수)
        departure_month: 출발 월
        companions: 동행인
        trip_repo: Trip Repository
        db: DB 세션

    Returns:
        StreamingResponse: SSE 스트리밍 응답

    Example:
        # JavaScript 클라이언트
        const eventSource = new EventSource('/api/v1/trips/generate?user_id=123&destination=제주도&purpose=관광');

        eventSource.addEventListener('message', (e) => {
            const data = JSON.parse(e.data);
            console.log(data);
        });

        eventSource.addEventListener('completed', (e) => {
            const data = JSON.parse(e.data);
            console.log('생성된 Trip:', data.trip);
            eventSource.close();
        });

        eventSource.addEventListener('error', (e) => {
            console.error('에러:', e.data);
            eventSource.close();
        });
    """
    try:
        # Command 생성
        command = CreateTripCommand(
            user_id=user_id,
            destination=destination,
            purpose=purpose,
            duration_nights=duration_nights,
            departure_month=departure_month,
            companions=companions,
        )

        # AI 클라이언트 생성
        ai_client = GeminiClient()

        # 스트리밍 생성
        return StreamingResponse(
            _stream_trip_generation(command, trip_repo, ai_client),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Nginx 버퍼링 비활성화
            },
        )

    except Exception as e:
        logger.error(f"트립 생성 스트리밍 시작 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"트립 생성을 시작할 수 없습니다: {str(e)}",
        )


# Pydantic 스키마 (Request Body 사용 시)
class TripGenerateRequest:
    """트립 생성 요청 스키마."""

    def __init__(
        self,
        destination: str,
        purpose: list[str],
        duration_nights: int | None = None,
        departure_month: int | None = None,
        companions: str | None = None,
    ):
        self.destination = destination
        self.purpose = purpose
        self.duration_nights = duration_nights
        self.departure_month = departure_month
        self.companions = companions


@router.post("/generate/body")
async def generate_trip_stream_body(
    request_data: TripGenerateRequest,
    user_id: str,  # 인증 토큰에서 추출
    trip_repo: TripRepository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """Request Body를 사용한 트립 생성 스트리밍.

    POST body에 데이터를 전송하는 방식.

    Args:
        request_data: 트립 생성 데이터
        user_id: 사용자 ID
        trip_repo: Trip Repository
        db: DB 세션

    Returns:
        StreamingResponse: SSE 스트리밍 응답
    """
    try:
        # Command 생성
        command = CreateTripCommand(
            user_id=user_id,
            destination=request_data.destination,
            purpose=request_data.purpose,
            duration_nights=request_data.duration_nights,
            departure_month=request_data.departure_month,
            companions=request_data.companions,
        )

        # AI 클라이언트 생성
        ai_client = GeminiClient()

        # 스트리밍 생성
        return StreamingResponse(
            _stream_trip_generation(command, trip_repo, ai_client),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    except Exception as e:
        logger.error(f"트립 생성 스트리밍 시작 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"트립 생성을 시작할 수 없습니다: {str(e)}",
        )