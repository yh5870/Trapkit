"""Repository Dependency Injection."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.trip_repository import TripRepository
from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository
from shared.config.database import get_db


def get_trip_repository(
    session: AsyncSession = Depends(get_db),
) -> TripRepository:
    """TripRepository 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 Repository 인스턴스를 제공합니다.

    Args:
        session: 비동기 데이터베이스 세션

    Returns:
        TripRepository 인스턴스

    Example:
        ```python
        @router.get("/trips")
        async def get_trips(
            trip_repo: TripRepository = Depends(get_trip_repository),
        ):
            trips = await trip_repo.find_by_user_id(user_id)
            return trips
        ```
    """
    return SQLAlchemyTripRepository(session)


# 타입 힌트 별칭 (코드 가독성 향상)
TripRepositoryDep = Annotated[TripRepository, Depends(get_trip_repository)]
