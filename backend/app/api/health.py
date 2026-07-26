"""헬스체크 API."""

from fastapi import APIRouter

from app.utils.logger import setup_logger

logger = setup_logger(__name__)
router = APIRouter()


# prefix="/health" 와 결합해 `/health` 와 `/health/` 를 모두 직접 처리한다.
# `@router.get("/")` 만 두면 정규 경로가 `/health/` 가 되어, 슬래시 없는
# `/health` 요청이 307 리다이렉트를 거친다. Render 헬스체크가 이 경로를
# 주기적으로 호출하므로 매번 불필요한 왕복이 발생하고, 리다이렉트를 따르지
# 않는 체커에서는 실패로 판정될 수 있다.
@router.get("")
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