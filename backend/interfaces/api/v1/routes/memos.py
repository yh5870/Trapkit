"""Memo CRUD 라우터.

Memo에 대한 CRUD 엔드포인트를 제공합니다.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from pydantic import BaseModel, Field

from app.domain.value_objects.memo_id import MemoId
from app.domain.value_objects.trip_id import TripId
from app.models.trip import Memo, Trip as TripModel


class MemoCreateRequest(BaseModel):
    """Memo 생성 요청 스키마."""

    trip_id: str = Field(..., description="Trip ID")
    content: str = Field(..., max_length=2000, description="메모 내용 (최대 2,000자)")


class MemoUpdateRequest(BaseModel):
    """Memo 수정 요청 스키마."""

    content: str = Field(..., max_length=2000, description="메모 내용 (최대 2,000자)")


from app.domain.models.trip import Trip
from app.domain.value_objects.trip_id import TripId
from app.utils.logger import setup_logger
from infrastructure.database.dependencies import get_memo_repository, get_trip_repository
from interfaces.api.dependencies.auth import get_current_user_id
from shared.config.database import get_db

logger = setup_logger(__name__)
router = APIRouter()


@router.get("/{trip_id}")
async def get_memos_by_trip_id(
    trip_id: str,
    user_id: str = Depends(get_current_user_id),
    memo_repo = Depends(get_memo_repository),
    trip_repo = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Trip ID로 모든 Memo 조회 (생성일 내림차순).

    Args:
        trip_id: Trip ID
        user_id: 사용자 ID (인증 톁에서 추출)
        memo_repo: Memo Repository (의존성 주입)
        trip_repo: Trip Repository (소유권 확인용)
        db: DB 세션

    Returns:
        Trip ID에 속한 Memo 리스트

    Raises:
        HTTPException: Trip을 찾을 수 없거나 접근 권한 없을 때

    Example:
        >>> response = client.get("/api/v1/memos/{trip_id}", headers=auth_headers)
        >>> data = response.json()
        >>> data["memos"]
    """
    try:
        # Trip 소유권 확인
        trip_id_obj = TripId.from_string(trip_id)
        trip = await trip_repo.find_by_id(trip_id_obj)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip ID {trip_id}를 찾을 수 없습니다.",
            )

        if trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Trip의 메모를 볼 권한이 없습니다.",
            )

        # Memo 조회
        memos = await memo_repo.find_by_trip_id(trip_id)

        return {
            "trip_id": trip_id,
            "memos": [
                {
                    "id": memo.id,
                    "trip_id": memo.trip_id,
                    "content": memo.content,
                    "created_at": memo.created_at.isoformat() if memo.created_at else None,
                    "updated_at": memo.updated_at.isoformat() if memo.updated_at else None,
                }
                for memo in memos
            ],
            "total": len(memos),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memo 조회에 실패했습니다: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memo 조회에 실패했습니다: {str(e)}",
        )


@router.post("")
async def create_memo(
    request_data: MemoCreateRequest,
    user_id: str = Depends(get_current_user_id),
    trip_repo = Depends(get_trip_repository),
    memo_repo = Depends(get_memo_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Memo 생성.

    Args:
        request_data: Memo 생성 데이터 (Pydantic 스키마)
        user_id: 사용자 ID (인증 톁에서 추출)
        trip_repo: Trip Repository (소유권 확인용)
        memo_repo: Memo Repository (저장용)
        db: DB 세션

    Returns:
        생성된 Memo

    Raises:
        HTTPException: 생성 실패 시

    Example:
        >>> response = client.post("/api/v1/memos", json={"trip_id": "...", "content": "..."}, headers=auth_headers)
        >>> data = response.json()
    """
    try:
        # Trip 소유권 확인
        trip_id_obj = TripId.from_string(request_data.trip_id)
        trip = await trip_repo.find_by_id(trip_id_obj)

        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip ID {request_data.trip_id}를 찾을 수 없습니다.",
            )

        if trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Trip에 메모를 추가할 권한이 없습니다.",
            )

        # 도메인 엔티티 생성
        memo = Memo.create(
            trip_id=request_data.trip_id,
            content=request_data.content,
        )

        # 저장
        saved = await memo_repo.save(memo)

        return {
            "id": saved.id,
            "trip_id": request_data.trip_id,
            "content": saved.content,
            "created_at": saved.created_at.isoformat() if saved.created_at else None,
            "updated_at": saved.updated_at.isoformat() if saved.updated_at else None,
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Memo 생성에 실패했습니다: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memo 생성에 실패했습니다: {str(e)}",
        )


@router.patch("/{memo_id}")
async def update_memo(
    memo_id: str,
    request_data: MemoUpdateRequest,
    user_id: str = Depends(get_current_user_id),
    memo_repo = Depends(get_memo_repository),
    trip_repo = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Memo 수정.

    Args:
        memo_id: Memo ID
        request_data: Memo 수정 데이터 (Pydantic 스키마)
        user_id: 사용자 ID (인증 톁에서 추출)
        memo_repo: Memo Repository (저장용)
        db: DB 세션

    Returns:
        수정된 Memo

    Raises:
        HTTPException: 수정 실패 시

    Example:
        >>> response = client.patch("/api/v1/memos/{memo_id}", json={"content": "..."}, headers=auth_headers)
        >>> data = response.json()
    """
    try:
        # Memo 조회
        memo = await memo_repo.find_by_id(memo_id)

        if memo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memo ID {memo_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip_id_obj = TripId.from_string(memo.trip_id)
        trip = await trip_repo.find_by_id(trip_id_obj)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 메모를 수정할 권한이 없습니다.",
            )

        # 업데이트 (불변 객체 패턴)
        updated = memo.update_content(request_data.content)

        # 저장
        saved = await memo_repo.save(updated)

        return {
            "id": saved.id,
            "trip_id": saved.trip_id,
            "content": saved.content,
            "created_at": saved.created_at.isoformat() if saved.created_at else None,
            "updated_at": saved.updated_at.isoformat() if saved.updated_at else None,
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Memo 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memo 수정에 실패했습니다: {str(e)}",
        )


@router.delete("/{memo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memo(
    memo_id: str,
    user_id: str = Depends(get_current_user_id),
    memo_repo = Depends(get_memo_repository),
    trip_repo = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
):
    """Memo 삭제.

    Args:
        memo_id: Memo ID
        user_id: 사용자 ID (인증 톁에서 추출)
        memo_repo: Memo Repository (삭제용)
        trip_repo: Trip Repository (소유권 확인용)
        db: DB 세션

    Raises:
        HTTPException: 삭제 실패 시

    Example:
        >>> response = client.delete("/api/v1/memos/{memo_id}", headers=auth_headers)
        >>> response.status_code == 204
    """
    try:
        # Memo 조회
        memo = await memo_repo.find_by_id(memo_id)

        if memo is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Memo ID {memo_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip_id_obj = TripId.from_string(memo.trip_id)
        trip = await trip_repo.find_by_id(trip_id_obj)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 메모를 삭제할 권한이 없습니다.",
            )

        # 삭제
        await memo_repo.delete(memo_id)

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Memo 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Memo 삭제에 실패했습니다: {str(e)}",
        )