"""트립/체크리스트/메모 API."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import SessionDep, UserDep, OptionalUserDep
from app.schemas.trip import (
    Category,
    Cautions,
    ChecklistItem,
    GenerateTripRequest,
    GenerateTripResponse,
    ImportTripsRequest,
    Memo,
    TripDetailResponse,
    TripListResponse,
    TripSummary,
    UpdateTripRequest,
)
from app.schemas.trip import ImportTripsResponse
from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.get("", response_model=TripListResponse)
async def get_trips(user: OptionalUserDep, db: SessionDep):
    """내 여행 목록."""
    # TODO: DB에서 사용자 여행 목록 조회
    logger.info(f"여행 목록 조회: {user.id if user else 'anonymous'}")

    # 임시 응답
    trips = [
        TripSummary(
            id="sapporo-ski",
            title="삿포로 스키 여행",
            meta="12월 · 4박 5일",
            progress={"checked": 8, "total": 26},
            status="ongoing",
        ),
        TripSummary(
            id="danang-family",
            title="다낭 가족 휴양",
            meta="7월 · 3박 4일",
            progress={"checked": 23, "total": 23},
            status="done",
        ),
    ]

    return TripListResponse(trips=trips)


@router.post("/generate", response_model=GenerateTripResponse)
async def generate_trip(body: GenerateTripRequest, user: OptionalUserDep, db: SessionDep):
    """AI 리스트 생성."""
    # TODO: AI 서비스 호출
    # result = await ai_service.generate_trip_list(body)
    logger.info(f"AI 리스트 생성 요청: {body.destination}, {body.purpose}")

    # 임시 응답
    categories = [
        Category(
            name="필수",
            items=[
                ChecklistItem(
                    id="c1-1",
                    name="여권",
                    quantity=None,
                    tip="유효기간 6개월 이상 확인",
                    baggage_flag=None,
                    source="ai",
                    checked=False,
                ),
                ChecklistItem(
                    id="c1-2",
                    name="보조배터리",
                    quantity="1개",
                    tip="추위에 배터리가 빨리 닳으므로 필수",
                    baggage_flag="carry_on_only",
                    source="ai",
                    checked=False,
                ),
            ],
        )
    ]

    cautions = [
        Cautions(
            category="기후",
            text="12월 삿포로는 평균 -4℃이며 폭설로 항공편이 지연될 수 있습니다.",
            confidence="stable",
        )
    ]

    return GenerateTripResponse(
        trip_title=f"{body.destination} 여행",
        categories=categories,
        cautions=cautions,
        baggage_summary=[
            {
                "item": "보조배터리",
                "rule": "위탁 불가, 기내 반입만 가능 (100Wh 이하)",
                "severity": "warning",
            }
        ],
        trip_id="new-trip-id" if user else None,
    )


@router.get("/{trip_id}", response_model=TripDetailResponse)
async def get_trip(trip_id: str, user: OptionalUserDep, db: SessionDep):
    """여행 상세."""
    # TODO: DB에서 여행 상세 조회
    logger.info(f"여행 상세 조회: {trip_id}")

    # 임시 응답
    return TripDetailResponse(
        trip_title="삿포로 스키 여행",
        meta="12월 · 4박 5일 · 친구 2명",
        progress={"checked": 8, "total": 26},
        categories=[],
        cautions=[],
        baggage_summary=[],
        memos=[],
    )


@router.patch("/{trip_id}", response_model=TripDetailResponse)
async def update_trip(trip_id: str, body: UpdateTripRequest, user: OptionalUserDep, db: SessionDep):
    """여행 제목 수정."""
    # TODO: DB에서 여행 제목 수정
    logger.info(f"여행 제목 수정: {trip_id}, {body.title}")
    return TripDetailResponse(
        trip_title=body.title or "삿포로 스키 여행",
        meta="12월 · 4박 5일",
        progress={"checked": 8, "total": 26},
        categories=[],
        cautions=[],
        baggage_summary=[],
        memos=[],
    )


@router.delete("/{trip_id}")
async def delete_trip(trip_id: str, user: OptionalUserDep, db: SessionDep):
    """여행 삭제."""
    # TODO: DB에서 여행 삭제
    logger.info(f"여행 삭제: {trip_id}")
    return {"message": "Trip deleted successfully"}


@router.post("/{trip_id}/items", response_model=ChecklistItem)
async def add_item(trip_id: str, body: BaseModel, user: OptionalUserDep, db: SessionDep):
    """항목 추가."""
    # TODO: DB에 항목 추가
    logger.info(f"항목 추가: {trip_id}")
    return ChecklistItem(
        id="new-item-id",
        name="새 항목",
        quantity=None,
        tip=None,
        baggage_flag=None,
        source="user",
        checked=False,
    )


@router.patch("/{trip_id}/items/{item_id}", response_model=ChecklistItem)
async def update_item(trip_id: str, item_id: str, body: BaseModel, user: OptionalUserDep, db: SessionDep):
    """항목 수정/체크 토글."""
    # TODO: DB에서 항목 수정
    logger.info(f"항목 수정: {trip_id}, {item_id}")
    return ChecklistItem(
        id=item_id,
        name="항목",
        quantity=None,
        tip=None,
        baggage_flag=None,
        source="user",
        checked=True,
    )


@router.delete("/{trip_id}/items/{item_id}")
async def delete_item(trip_id: str, item_id: str, user: OptionalUserDep, db: SessionDep):
    """항목 삭제."""
    # TODO: DB에서 항목 삭제
    logger.info(f"항목 삭제: {trip_id}, {item_id}")
    return {"message": "Item deleted successfully"}


@router.post("/{trip_id}/memos", response_model=Memo)
async def add_memo(trip_id: str, body: BaseModel, user: OptionalUserDep, db: SessionDep):
    """메모 추가."""
    # TODO: DB에 메모 추가
    logger.info(f"메모 추가: {trip_id}")
    return Memo(id="new-memo-id", content="새 메모", updated_at="방금")


@router.patch("/{trip_id}/memos/{memo_id}", response_model=Memo)
async def update_memo(trip_id: str, memo_id: str, body: BaseModel, user: OptionalUserDep, db: SessionDep):
    """메모 수정."""
    # TODO: DB에서 메모 수정
    logger.info(f"메모 수정: {trip_id}, {memo_id}")
    return Memo(id=memo_id, content="수정된 메모", updated_at="방금")


@router.delete("/{trip_id}/memos/{memo_id}")
async def delete_memo(trip_id: str, memo_id: str, user: OptionalUserDep, db: SessionDep):
    """메모 삭제."""
    # TODO: DB에서 메모 삭제
    logger.info(f"메모 삭제: {trip_id}, {memo_id}")
    return {"message": "Memo deleted successfully"}


@router.post("/import", response_model=ImportTripsResponse)
async def import_trips(
    body: ImportTripsRequest,
    user: OptionalUserDep,
    db: SessionDep,
):
    """비로그인 로컬 트립 이관.

    JSON 형식으로 여행 데이터를 받아 DB에 저장합니다.
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )

    from uuid import uuid4
    from app.domain.models.trip import Trip
    from app.domain.models.item import Item, Memo
    from app.domain.value_objects.trip_id import TripId
    from infrastructure.database.dependencies import (
        get_trip_repository,
        get_item_repository,
        get_memo_repository,
    )

    logger.info(f"트립 import 요청: {len(body.trips)}개, user_id={user.id}")

    trip_repo = get_trip_repository(db)
    item_repo = get_item_repository(db)
    memo_repo = get_memo_repository(db)

    imported_trip_ids = []

    for trip_data in body.trips:
        # Trip 도메인 엔티티 생성
        trip = Trip.create(
            title=trip_data.title,
            destination=trip_data.destination,
            purpose=trip_data.purpose,
            user_id=user.id,
            duration_nights=trip_data.duration_nights,
            departure_month=trip_data.departure_month,
            companions=trip_data.companions,
        )

        # cautions와 baggage_summary 업데이트
        trip = trip.update(
            cautions=[caution.model_dump() for caution in trip_data.cautions],
            baggage_summary=trip_data.baggage_summary,
        )

        # Trip 저장
        saved_trip = await trip_repo.save(trip)
        imported_trip_ids.append(str(saved_trip.id.value))

        # Categories (Items) 저장
        for category in trip_data.categories:
            for idx, item_data in enumerate(category.items):
                item = Item.create(
                    trip_id=saved_trip.id,
                    category=category.name,
                    name=item_data.name,
                    quantity=item_data.quantity,
                    tip=item_data.tip,
                    baggage_flag=item_data.baggage_flag,
                    source=item_data.source,
                )
                # sort_order 설정
                item = item.update(sort_order=idx, checked=item_data.checked)
                await item_repo.save(item)

        # Memos 저장
        for memo_data in trip_data.memos:
            memo = Memo.create(
                trip_id=saved_trip.id,
                content=memo_data.content,
            )
            await memo_repo.save(memo)

        logger.debug(f"Trip 저장 완료: {saved_trip.id.value}")

    logger.info(f"트립 import 완료: {len(imported_trip_ids)}개")

    return ImportTripsResponse(
        imported_count=len(imported_trip_ids),
        imported_trip_ids=imported_trip_ids,
    )