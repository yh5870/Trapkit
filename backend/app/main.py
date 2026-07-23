"""FastAPI 앱 진입점."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, baggage, health, trips, trip_domain
from app.config import settings
from app.core.database import init_db, close_db
from app.utils.logger import setup_logger
from interfaces.api.v1.routes import trips as streaming_trips

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 라이프사이클 관리."""
    logger.info("Trapkit Backend 시작 중...")
    await init_db()
    yield
    await close_db()
    logger.info("Trapkit Backend 종료 중...")


app = FastAPI(
    title="Trapkit API",
    description="AI 여행 준비물 리스트 & 수화물 규정 체크 서비스",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(trips.router, prefix="/api/trips", tags=["Trips"])
app.include_router(trip_domain.router, prefix="/api/v1/trips", tags=["Trips V1 (Domain)"])
app.include_router(streaming_trips.router, prefix="/api/v1/trips", tags=["Trips V1 (Streaming)"])
app.include_router(baggage.router, prefix="/api/baggage", tags=["Baggage"])


@app.get("/")
async def root():
    """루트 엔드포인트."""
    return {
        "name": "Trapkit API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs",
    }