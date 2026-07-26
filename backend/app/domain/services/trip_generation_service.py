"""Trip 생성 도메인 서비스.

AI를 통한 트립 생성 로직을 담당하는 도메인 서비스.
실제 AI 호출은 B개발자의 AIClient를 통해 이루어집니다.
"""

from abc import ABC, abstractmethod

from app.application.commands.create_trip import CreateTripCommand
from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository


class AIClient(ABC):
    """AI 클라이언트 인터페이스 (B개발자가 구현)."""

    @abstractmethod
    async def generate_trip_content(self, command: CreateTripCommand) -> dict:
        """AI를 통해 트립 콘텐츠 생성."""
        pass


class TripGenerationService:
    """Trip 생성 도메인 서비스."""

    def __init__(self, trip_repository: TripRepository, ai_client: AIClient) -> None:
        """초기화.

        Args:
            trip_repository: Trip 저장소
            ai_client: AI 클라이언트
        """
        self.trip_repository = trip_repository
        self.ai_client = ai_client

    async def generate(self, command: CreateTripCommand) -> Trip:
        """AI를 통해 Trip 생성.

        Args:
            command: Trip 생성 Command

        Returns:
            생성된 Trip 엔티티

        Process:
            1. AI로부터 트립 콘텐츠 생성 (cautions, baggage_summary)
            2. Trip 엔티티 생성
            3. 저장소에 저장
            4. 저장된 Trip 반환
        """
        # 1. AI로부터 트립 콘텐츠 생성
        ai_content = await self.ai_client.generate_trip_content(command)

        # 2. Trip 엔티티 생성
        trip = Trip.create(
            title=command.destination,  # 기본 제목은 여행지로
            destination=command.destination,
            purpose=command.purpose,
            user_id=command.user_id,
            duration_nights=command.duration_nights,
            departure_month=command.departure_month,
            companions=command.companions,
            cautions=ai_content.get("cautions", []),
            baggage_summary=ai_content.get("baggage_summary", []),
        )

        # 3. 저장소에 저장
        await self.trip_repository.save(trip)

        # 4. 저장된 Trip 반환
        return trip