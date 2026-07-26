"""pytest 설정."""

import asyncio
import os
from typing import Any, AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 테스트용 DB URL (환경변수 오버라이드 - 앱 초기화 전에 설정)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "test"
os.environ["JWT_SECRET"] = "test-secret-key-at-least-32-chars"

from app.main import app
from shared.config.database import get_db

# 모든 ORM 모델 import (테스트 DB에 테이블 생성용)
import infrastructure.database.models.item_model
import infrastructure.database.models.memo_model
import infrastructure.database.models.profile_model
import infrastructure.database.models.trip_model
from shared.config.database import Base


# 테스트용 DB 엔진 (SQLite는 pool 설정 불필요)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_test_db() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 DB 세션."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """이벤트 루프."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """테스트용 HTTP 클라이언트."""
    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 DB 세션."""
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    # 테이블 정리
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
def test_user():
    """테스트용 사용자."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "nickname": "Test User",
    }