"""Item CRUD 라우터.

Item에 대한 CRUD 엔드포인트를 제공합니다.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.commands.item_commands import (
    AddItemCommand,
    CheckItemCommand,
    UpdateItemCommand,
    UpdateSortOrderCommand,
)
from app.domain.models.item import Item
from app.domain.models.trip import Trip
from app.domain.value_objects.item_id import ItemId
from app.domain.value_objects.trip_id import TripId
from app.utils.logger import setup_logger
from infrastructure.database.dependencies import get_item_repository, get_trip_repository
from shared.config.database import get_db

logger = setup_logger(__name__)
router = APIRouter()


def _format_sse_event(data: dict[str, Any], event_type: str = "message") -> str:
    """Server-Sent Events 이벤트 포맷팅."""
    event_str = f"event: {event_type}\n"
    data_str = __import__('json').json.dumps(data, ensure_ascii=False, default=str)
    event_str += f"data: {data_str}\n\n"
    return event_str


@router.get("/{trip_id}")
async def get_items_by_trip_id(
    trip_id: str,
    user_id: str,
    item_repo: get_item_repository = Depends(get_item_repository),
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Trip ID로 모든 Item 조회.

    Args:
        trip_id: Trip ID
        user_id: 사용자 ID (인증 토큰에서 추출)
        item_repo: Item Repository (의존성 주입)
        trip_repo: Trip Repository (소유권 확인용)
        db: DB 세션

    Returns:
        Trip ID에 속한 Item 리스트

    Raises:
        HTTPException: Trip을 찾을 수 없거나 접근 권한 없을 때

    Example:
        >>> response = client.get("/api/v1/items/{trip_id}", headers=auth_headers)
        >>> data = response.json()
        >>> data["items"]
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
                detail="이 Trip에 접근할 권한이 없습니다.",
            )

        # Item 조회
        items = await item_repo.find_by_trip_id(trip_id_obj)

        return {
            "trip_id": trip_id,
            "items": [
                {
                    "id": str(item.id.value),
                    "category": item.category,
                    "name": item.name,
                    "quantity": item.quantity,
                    "tip": item.tip,
                    "baggage_flag": item.baggage_flag,
                    "source": item.source,
                    "checked": item.checked,
                    "sort_order": item.sort_order,
                }
                for item in items
            ],
            "total": len(items),
            "checked": sum(1 for item in items if item.checked),
            "pending": sum(1 for item in items if not item.checked),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item 조회 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Item 조회에 실패했습니다: {str(e)}",
        )


@router.post("")
async def create_item(
    request_data: AddItemCommand,
    user_id: str,
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    item_repo: get_item_repository = Depends(get_item_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Item 생성.

    Args:
        request_data: Item 생성 데이터
        user_id: 사용자 ID (인증 토큰에서 추출)
        trip_repo: Trip Repository (소유권 확인용)
        item_repo: Item Repository (저장용)
        db: DB 세션

    Returns:
        생성된 Item

    Raises:
        HTTPException: 생성 실패 시

    Example:
        >>> response = client.post("/api/v1/items", json=request_data, headers=auth_headers)
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
                detail="이 Trip에 추가할 권한이 없습니다.",
            )

        # 도메인 엔티티 생성
        item = Item.create(
            trip_id=trip_id_obj,
            category=request_data.category,
            name=request_data.name,
            quantity=request_data.quantity,
            tip=request_data.tip,
            baggage_flag=request_data.baggage_flag,
            source=request_data.source,
        )

        # 저장
        saved = await item_repo.save(item)

        return {
            "id": str(saved.id.value),
            "trip_id": request_data.trip_id,
            "category": saved.category,
            "name": saved.name,
            "quantity": saved.quantity,
            "tip": saved.tip,
            "baggage_flag": saved.baggage_flag,
            "source": saved.source,
            "checked": saved.checked,
            "sort_order": saved.sort_order,
            "created_at": saved.created_at.isoformat(),
            "updated_at": saved.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item 생성 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Item 생성에 실패했습니다: {str(e)}",
        )


@router.patch("/{item_id}")
async def update_item(
    item_id: str,
    request_data: UpdateItemCommand,
    user_id: str,
    item_repo: get_item_repository = Depends(get_item_repository),
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Item 수정.

    Args:
        item_id: Item ID
        request_data: Item 수정 데이터
        user_id: 사용자 ID (인증 토큰에서 추출)
        item_repo: Item Repository (저장용)
        db: DB 세션

    Returns:
        수정된 Item

    Raises:
        HTTPException: 수정 실패 시

    Example:
        >>> response = client.patch("/api/v1/items/{item_id}", json=request_data, headers=auth_headers)
        >>> data = response.json()
    """
    try:
        # Item 조회
        item_id_obj = ItemId.from_string(item_id)
        item = await item_repo.find_by_id(item_id_obj)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item ID {item_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip = await trip_repo.find_by_id(item.trip_id)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Item을 수정할 권한이 없습니다.",
            )

        # 업데이트 (불변 객체 패턴)
        updated = item.update(
            name=request_data.name,
            quantity=request_data.quantity,
            tip=request_data.tip,
            baggage_flag=request_data.baggage_flag,
            checked=request_data.checked,
        )

        # 저장
        saved = await item_repo.save(updated)

        return {
            "id": str(saved.id.value),
            "trip_id": str(saved.trip_id.value),
            "category": saved.category,
            "name": saved.name,
            "quantity": saved.quantity,
            "tip": saved.tip,
            "baggage_flag": saved.baggage_flag,
            "source": saved.source,
            "checked": saved.checked,
            "sort_order": saved.sort_order,
            "created_at": saved.created_at.isoformat(),
            "updated_at": saved.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item 수정 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Item 수정에 실패했습니다: {str(e)}",
        )


@router.delete("/{item_id}")
async def delete_item(
    item_id: str,
    user_id: str,
    item_repo: get_item_repository = Depends(get_item_repository),
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Item 삭제.

    Args:
        item_id: Item ID
        user_id: 사용자 ID (인증 톁에서 추출)
        item_repo: Item Repository (삭제용)
        db: DB 세션

    Returns:
        204 No Content

    Raises:
        HTTPException: 삭제 실패 시

    Example:
        >>> response = client.delete("/api/v1/items/{item_id}", headers=auth_headers)
        >>> response.status_code == 204
    """
    try:
        # Item 조회
        item_id_obj = ItemId.from_string(item_id)
        item = await item_repo.find_by_id(item_id_obj)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item ID {item_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip = await trip_repo.find_by_id(item.trip_id)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Item을 삭제할 권한이 없습니다.",
            )

        # 삭제
        await item_repo.delete(item_id_obj)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item 삭제 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Item 삭제에 실패했습니다: {str(e)}",
        )


@router.patch("/{item_id}/check")
async def check_item(
    item_id: str,
    command: CheckItemCommand,
    user_id: str,
    item_repo: get_item_repository = Depends(get_item_repository),
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Item 체크/언체크 박스.

    Args:
        item_id: Item ID
        command: 체크박스 Command
        user_id: 사용자 ID (인증 톁에서 추출)
        item_repo: Item Repository (저장용)
        db: DB 세션

    Returns:
        체크박스 처리된 Item

    Raises:
        HTTPException: 체크박스 실패 시

    Example:
        >>> response = client.patch("/api/v1/items/{item_id}/check", json=command, headers=auth_headers)
        >>> data = response.json()
    """
    try:
        # Item 조회
        item_id_obj = ItemId.from_string(item_id)
        item = await item_repo.find_by_id(item_id_obj)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item ID {item_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip = await trip_repo.find_by_id(item.trip_id)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Item에 체크박스할 권한이 없습니다.",
            )

        # 체크박스 처리
        if command.checked:
            updated = item.check()
        else:
            updated = item.uncheck()

        # 저장
        saved = await item_repo.save(updated)

        return {
            "id": str(saved.id.value),
            "trip_id": str(saved.trip_id.value),
            "category": saved.category,
            "name": saved.name,
            "quantity": saved.quantity,
            "tip": saved.tip,
            "baggage_flag": saved.baggage_flag,
            "source": saved.source,
            "checked": saved.checked,
            "sort_order": saved.sort_order,
            "created_at": saved.created_at.isoformat(),
            "updated_at": saved.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Item 체크박스 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Item 체크박스에 실패했습니다: {str(e)}",
        )


@router.patch("/{item_id}/sort")
async def update_sort_order(
    item_id: str,
    command: UpdateSortOrderCommand,
    user_id: str,
    item_repo: get_item_repository = Depends(get_item_repository),
    trip_repo: get_trip_repository = Depends(get_trip_repository),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Item 정렬 순서 변경.

    Args:
        item_id: Item ID
        command: 정렬 순서 변경 Command
        user_id: 사용자 ID (인증 톁에서 추출)
        item_repo: Item Repository (저장용)
        db: DB 세션

    Returns:
        정렬 순서 변경된 Item

    Raises:
        HTTPException: 변경 실패 시

    Example:
        >>> response = client.patch("/api/v1/items/{item_id}/sort", json=command, headers=auth_headers)
        >>> data = response.json()
    """
    try:
        # Item 조회
        item_id_obj = ItemId.from_string(item_id)
        item = await item_repo.find_by_id(item_id_obj)

        if item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item ID {item_id}를 찾을 수 없습니다.",
            )

        # 소유권 확인 (Trip 조회)
        trip = await trip_repo.find_by_id(item.trip_id)
        if trip is None or trip.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="이 Item의 정렬 순서를 변경할 권한이 없습니다.",
            )

        # 정렬 순서 변경
        updated = item.sort_order_up(command.new_order)

        # 저장
        saved = await item_repo.save(updated)

        return {
            "id": str(saved.id.value),
            "trip_id": str(saved.trip_id.value),
            "category": saved.category,
            "name": saved.name,
            "quantity": saved.quantity,
            "tip": saved.tip,
            "baggage_flag": saved.baggage_flag,
            "source": saved.source,
            "checked": saved.checked,
            "sort_order": saved.sort_order,
            "created_at": saved.created_at.isoformat(),
            "updated_at": saved.updated_at.isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"정렬 순서 변경 실패: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"정렬 순서 변경에 실패했습니다: {str(e)}",
        )