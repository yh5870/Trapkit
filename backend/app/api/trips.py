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
    Memo,
    TripDetailResponse,
    TripListResponse,
    TripSummary,
    UpdateTripRequest,
)
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


@router.post("/import")
async def import_trips(body: BaseModel, user: OptionalUserDep, db: SessionDep):
    """비로그인 로컬 트립 이관."""
    # TODO: 비로그인 트립을 사용자 계정으로 이관
    logger.info("트립 이관 요청")
    return {"message": "Trips imported successfully"}