"""SQLAlchemy Trip Repository Implementation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository
from app.domain.value_objects.trip_id import TripId
from infrastructure.database.models.trip_model import TripModel


class SQLAlchemyTripRepository(TripRepository):
    """TripRepository의 SQLAlchemy 구현."""

    def __init__(self, session: AsyncSession) -> None:
        """초기화.

        Args:
            session: 비동기 데이터베이스 세션
        """
        self.session = session

    async def save(self, trip: Trip) -> Trip:
        """Trip 저장.

        Args:
            trip: 저장할 Trip 도메인 엔티티

        Returns:
            저장된 Trip 엔티티
        """
        model = self._to_infrastructure(trip)

        # 이미 존재하는지 확인
        existing = await self.session.execute(
            select(TripModel).where(TripModel.id == str(trip.id.value))
        )
        if existing.scalar_one_or_none():
            # 업데이트
            existing_model = existing.scalar_one_or_none()
            existing_model.title = trip.title
            existing_model.destination = trip.destination
            existing_model.purpose = trip.purpose
            existing_model.duration_nights = trip.duration_nights
            existing_model.departure_month = trip.departure_month
            existing_model.companions = trip.companions
            existing_model.cautions = trip.cautions
            existing_model.baggage_summary = trip.baggage_summary
            self.session.add(existing_model)
        else:
            # 새로 생성
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return self._to_domain(model)

    async def find_by_id(self, trip_id: TripId) -> Trip | None:
        """ID로 Trip 조회.

        Args:
            trip_id: 조회할 Trip ID

        Returns:
            Trip 엔티티 또는 None
        """
        result = await self.session.execute(
            select(TripModel)
            .options(selectinload(TripModel.items))
            .where(TripModel.id == str(trip_id.value))
        )
        model = result.scalar_one_or_none()

        return self._to_domain(model) if model else None

    async def find_by_user_id(self, user_id: str) -> list[Trip]:
        """사용자 ID로 모든 Trip 조회.

        Args:
            user_id: 사용자 ID

        Returns:
            Trip 엔티티 리스트 (생성일 기준 내림차순)
        """
        result = await self.session.execute(
            select(TripModel)
            .options(selectinload(TripModel.items))
            .where(TripModel.user_id == user_id)
            .order_by(TripModel.created_at.desc())
        )
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def delete(self, trip_id: TripId) -> None:
        """Trip 삭제.

        Args:
            trip_id: 삭제할 Trip ID
        """
        result = await self.session.execute(
            select(TripModel).where(TripModel.id == str(trip_id.value))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.commit()

    def _to_domain(self, model: TripModel) -> Trip:
        """ORM 모델을 도메인 엔티티로 변환.

        Args:
            model: TripModel ORM 인스턴스

        Returns:
            Trip 도메인 엔티티
        """
        return Trip(
            id=TripId(UUID(model.id)),
            title=model.title,
            destination=model.destination,
            purpose=list(model.purpose) if isinstance(model.purpose, list) else model.purpose,
            user_id=model.user_id,
            duration_nights=model.duration_nights,
            departure_month=model.departure_month,
            companions=model.companions,
            cautions=list(model.cautions) if isinstance(model.cautions, list) else model.cautions,
            baggage_summary=list(model.baggage_summary) if isinstance(model.baggage_summary, list) else model.baggage_summary,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_infrastructure(self, trip: Trip) -> TripModel:
        """도메인 엔티티를 ORM 모델로 변환.

        Args:
            trip: Trip 도메인 엔티티

        Returns:
            TripModel ORM 인스턴스
        """
        return TripModel(
            id=str(trip.id.value),
            user_id=trip.user_id,
            title=trip.title,
            destination=trip.destination,
            purpose=trip.purpose,
            duration_nights=trip.duration_nights,
            departure_month=trip.departure_month,
            companions=trip.companions,
            cautions=trip.cautions,
            baggage_summary=trip.baggage_summary,
        )