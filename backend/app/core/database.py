"""DB 세션 관리."""

from collections.abc import AsyncGenerator
from typing import AsyncGenerator as AsyncGenType

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# 세션 팩토리
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenType[AsyncSession, None]:
    """DB 세션 의존성."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """DB 초기화 (테이블 생성)."""
    # TODO: Alembic 마이그레이션 사용
    # Base.metadata.create_all(bind=engine)
    pass


async def close_db() -> None:
    """DB 연결 종료."""
    await engine.dispose()