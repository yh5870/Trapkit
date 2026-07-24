"""Repository Dependency Injection."""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.trip_repository import TripRepository
from app.domain.repositories.item_repository import ItemRepository
from app.domain.repositories.memo_repository import MemoRepository
from app.domain.repositories.baggage_rule_repository import BaggageRuleRepository
from app.domain.repositories.user_repository import UserRepository
from infrastructure.database.repositories.sqlalchemy_trip_repository import SQLAlchemyTripRepository
from infrastructure.database.repositories.sqlalchemy_item_repository import SQLAlchemyItemRepository
from infrastructure.database.repositories.sqlalchemy_memo_repository import SQLAlchemyMemoRepository
from infrastructure.database.repositories.sqlalchemy_baggage_rule_repository import SQLAlchemyBaggageRuleRepository
from infrastructure.database.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
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


def get_baggage_rule_repository(
    session: AsyncSession = Depends(get_db),
) -> BaggageRuleRepository:
    """BaggageRuleRepository 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 Repository 인스턴스를 제공합니다.

    Args:
        session: 비동기 데이터베이스 세션

    Returns:
        BaggageRuleRepository 인스턴스

    Example:
        ```python
        @router.post("/baggage/check")
        async def check_baggage(
            baggage_repo: BaggageRuleRepository = Depends(get_baggage_rule_repository),
        ):
            rule = await baggage_repo.find_by_key("laptop")
            return rule
        ```
    """
    return SQLAlchemyBaggageRuleRepository(session)


def get_item_repository(
    session: AsyncSession = Depends(get_db),
) -> ItemRepository:
    """ItemRepository 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 Repository 인스턴스를 제공합니다.

    Args:
        session: 비동기 데이터베이스 세션

    Returns:
        ItemRepository 인스턴스

    Example:
        ```python
        @router.get("/items/{trip_id}")
        async def get_items(
            trip_id: str,
            item_repo: ItemRepository = Depends(get_item_repository),
        ):
            items = await item_repo.find_by_trip_id(TripId.from_string(trip_id))
            return items
        ```
    """
    return SQLAlchemyItemRepository(session)


def get_user_repository(
    session: AsyncSession = Depends(get_db),
) -> UserRepository:
    """UserRepository 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 Repository 인스턴스를 제공합니다.

    Args:
        session: 비동기 데이터베이스 세션

    Returns:
        UserRepository 인스턴스

    Example:
        ```python
        @router.post("/signup")
        async def signup(
            body: SignupRequest,
            user_repo: UserRepository = Depends(get_user_repository),
        ):
            user = await user_repo.save(body.email, hash_password(body.password), body.nickname)
            return UserResponse.from_dict(user)
        ```
    """
    return SQLAlchemyProfileRepository(session)


def get_memo_repository(
    session: AsyncSession = Depends(get_db),
) -> MemoRepository:
    """MemoRepository 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 Repository 인스턴스를 제공합니다.

    Args:
        session: 비동기 데이터베이스 세션

    Returns:
        MemoRepository 인스턴스

    Example:
        ```python
        @router.get("/trips/{trip_id}/memos")
        async def get_memos(
            trip_id: str,
            memo_repo: MemoRepository = Depends(get_memo_repository),
        ):
            memos = await memo_repo.find_by_trip_id(TripId.from_string(trip_id))
            return memos
        ```
    """
    return SQLAlchemyMemoRepository(session)


# 타입 힌트 별칭 (코드 가독성 향상)
TripRepositoryDep = Annotated[TripRepository, Depends(get_trip_repository)]
ItemRepositoryDep = Annotated[ItemRepository, Depends(get_item_repository)]
MemoRepositoryDep = Annotated[MemoRepository, Depends(get_memo_repository)]
BaggageRuleRepositoryDep = Annotated[BaggageRuleRepository, Depends(get_baggage_rule_repository)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]