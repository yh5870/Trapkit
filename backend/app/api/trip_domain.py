"""Trip 도메인 기반 API 라우터.

A개발자가 정의한 도메인 모델과 Repository를 사용하는 API 엔드포인트입니다.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import UserDep
from app.application.services.trip_query_service import TripQueryService
from app.domain.models.trip import Trip
from app.domain.repositories.trip_repository import TripRepository
from app.domain.value_objects.trip_id import TripId
from app.schemas.trip_domain import (
    TripCreate,
    TripListResponse,
    TripResponse,
    TripUpdate,
)
from app.utils.logger import setup_logger
from infrastructure.database.dependencies import get_trip_repository
from shared.config.database import get_db

logger = setup_logger(__name__)
router = APIRouter()


@router.get("", response_model=TripListResponse)
async def get_user_trips(
    user: UserDep,
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> TripListResponse:
    """사용자의 모든 Trip 조회.

    Args:
        user: 인증된 사용자
        trip_repo: Trip Repository (의존성 주입)

    Returns:
        TripListResponse: 사용자의 Trip 목록

    Raises:
        HTTPException: 조회 실패 시
    """
    try:
        query_service = TripQueryService(trip_repo)
        trips = await query_service.get_user_trips(user.id)

        trip_responses = [
            TripResponse(
                id=str(trip.id.value),
                title=trip.title,
                destination=trip.destination,
                purpose=trip.purpose,
                user_id=trip.user_id,
                duration_nights=trip.duration_nights,
                departure_month=trip.departure_month,
                companions=trip.companions,
                cautions=trip.cautions,
                baggage_summary=trip.baggage_summary,
                created_at=trip.created_at,
                updated_at=trip.updated_at,
            )
            for trip in trips
        ]

        return TripListResponse(trips=trip_responses, total=len(trip_responses))

    except Exception as e:
        logger.error(f"Trip 목록 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trip 목록 조회에 실패했습니다.",
        )


@router.get("/{trip_id}", response_model=TripResponse)
async def get_trip_by_id(
    trip_id: str,
    user: UserDep,
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> TripResponse:
    """ID로 Trip 조회.

    Args:
        trip_id: Trip ID
        user: 인증된 사용자
        trip_repo: Trip Repository (의존성 주입)

    Returns:
        TripResponse: Trip 상세 정보

    Raises:
        HTTPException: Trip을 찾을 수 없거나 접근 권한이 없을 때
    """
    try:
        query_service = TripQueryService(trip_repo)
        trip = await query_service.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip ID {trip_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인
        if trip.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Trip에 접근할 권한이 없습니다.",
            )

        return TripResponse(
            id=str(trip.id.value),
            title=trip.title,
            destination=trip.destination,
            purpose=trip.purpose,
            user_id=trip.user_id,
            duration_nights=trip.duration_nights,
            departure_month=trip.departure_month,
            companions=trip.companions,
            cautions=trip.cautions,
            baggage_summary=trip.baggage_summary,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trip 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trip 조회에 실패했습니다.",
        )


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripCreate,
    user: UserDep,
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> TripResponse:
    """새 Trip 생성.

    Args:
        trip_data: Trip 생성 데이터
        user: 인증된 사용자
        trip_repo: Trip Repository (의존성 주입)

    Returns:
        TripResponse: 생성된 Trip

    Raises:
        HTTPException: 생성 실패 시
    """
    try:
        # 도메인 엔티티 생성
        trip = Trip.create(
            title=trip_data.title,
            destination=trip_data.destination,
            purpose=trip_data.purpose,
            user_id=user.id,
            duration_nights=trip_data.duration_nights,
            departure_month=trip_data.departure_month,
            companions=trip_data.companions,
        )

        # 주의사항과 수화물 요약이 있는 경우 업데이트
        if trip_data.cautions:
            for caution in trip_data.cautions:
                trip = trip.add_caution(caution)

        if trip_data.baggage_summary:
            trip = trip.update_baggage_summary(trip_data.baggage_summary)

        # 저장
        saved_trip = await trip_repo.save(trip)

        return TripResponse(
            id=str(saved_trip.id.value),
            title=saved_trip.title,
            destination=saved_trip.destination,
            purpose=saved_trip.purpose,
            user_id=saved_trip.user_id,
            duration_nights=saved_trip.duration_nights,
            departure_month=saved_trip.departure_month,
            companions=saved_trip.companions,
            cautions=saved_trip.cautions,
            baggage_summary=saved_trip.baggage_summary,
            created_at=saved_trip.created_at,
            updated_at=saved_trip.updated_at,
        )

    except Exception as e:
        logger.error(f"Trip 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trip 생성에 실패했습니다.",
        )


@router.patch("/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: str,
    trip_data: TripUpdate,
    user: UserDep,
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> TripResponse:
    """Trip 수정.

    Args:
        trip_id: Trip ID
        trip_data: Trip 수정 데이터
        user: 인증된 사용자
        trip_repo: Trip Repository (의존성 주입)

    Returns:
        TripResponse: 수정된 Trip

    Raises:
        HTTPException: Trip을 찾을 수 없거나 접근 권한이 없을 때
    """
    try:
        query_service = TripQueryService(trip_repo)
        trip = await query_service.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip ID {trip_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인
        if trip.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Trip을 수정할 권한이 없습니다.",
            )

        # 업데이트 (불변 객체 패턴으로 새 인스턴스 생성)
        updated_trip = trip.update(
            title=trip_data.title,
            destination=trip_data.destination,
            purpose=trip_data.purpose,
            duration_nights=trip_data.duration_nights,
            departure_month=trip_data.departure_month,
            companions=trip_data.companions,
            cautions=trip_data.cautions,
            baggage_summary=trip_data.baggage_summary,
        )

        # 저장
        saved_trip = await trip_repo.save(updated_trip)

        return TripResponse(
            id=str(saved_trip.id.value),
            title=saved_trip.title,
            destination=saved_trip.destination,
            purpose=saved_trip.purpose,
            user_id=saved_trip.user_id,
            duration_nights=saved_trip.duration_nights,
            departure_month=saved_trip.departure_month,
            companions=saved_trip.companions,
            cautions=saved_trip.cautions,
            baggage_summary=saved_trip.baggage_summary,
            created_at=saved_trip.created_at,
            updated_at=saved_trip.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trip 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trip 수정에 실패했습니다.",
        )


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: str,
    user: UserDep,
    trip_repo: TripRepository = Depends(get_trip_repository),
) -> None:
    """Trip 삭제.

    Args:
        trip_id: Trip ID
        user: 인증된 사용자
        trip_repo: Trip Repository (의존성 주입)

    Raises:
        HTTPException: Trip을 찾을 수 없거나 접근 권한이 없을 때
    """
    try:
        query_service = TripQueryService(trip_repo)
        trip = await query_service.get_trip_by_id(trip_id)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip ID {trip_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인
        if trip.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Trip을 삭제할 권한이 없습니다.",
            )

        # 삭제
        await trip_repo.delete(trip.id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trip 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Trip 삭제에 실패했습니다.",
        )
