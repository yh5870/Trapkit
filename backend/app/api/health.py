"""헬스체크 API."""

from fastapi import APIRouter

from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


@router.get("/")
async def health_check():
    """서버 상태 확인."""
    return {
        "status": "healthy",
        "service": "trapkit-backend",
    }


@router.get("/db")
async def db_check():
    """DB 연결 확인."""
    # TODO: 실제 DB 연결 확인
    return {"status": "db_connected", "service": "trapkit-backend"}