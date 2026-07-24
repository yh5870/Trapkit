"""Database configuration and session management.

비동기 PostgreSQL 연결 및 세션 팩토리를 제공합니다.
FastAPI의 의존성 주입(DI)을 통해 요청마다 독립된 DB 세션을 제공합니다.
"""

import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """모든 ORM 모델의 기본 클래스."""


# 비동기 엔진 생성 (DB별 호환성 고려)
_db_url = settings.DATABASE_URL

# SQLite는 pool 설정을 지원하지 않음
engine_kwargs = {
    "echo": settings.ENVIRONMENT == "development",
}

# PostgreSQL만 pool 설정 추가
if "postgresql" in _db_url:
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })

# Supabase는 SSL 필수 (인증서 검증 비활성화)
if "supabase.co" in _db_url:
    # 인증서 검증 비활성화 SSL 컨텍스트 생성
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine_kwargs.update({
        "connect_args": {
            "ssl": ssl_context,
        }
    })

engine = create_async_engine(_db_url, **engine_kwargs)

# 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # 커밋 후 객체 접근 가능
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """데이터베이스 세션 의존성 주입.

    FastAPI의 Depends()로 사용하여 요청마다 독립된 세션을 제공합니다.

    Yields:
        AsyncSession: 데이터베이스 세션

    Example:
        ```python
        @router.get("/trips")
        async def get_trips(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(TripModel))
            return result.scalars().all()
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """데이터베이스 초기화.

    개발용으로만 사용. 실제 배포에서는 Alembic 마이그레이션을 사용하세요.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)