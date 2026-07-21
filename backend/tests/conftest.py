"""pytest 설정."""

import asyncio
from typing import Any, AsyncGenerator, Generator

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import get_db
from app.models.user import User


# 테스트용 DB 엔진
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
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def test_user() -> User:
    """테스트용 사용자."""
    return User(
        id="test-user-id",
        email="test@example.com",
        password_hash="hashed_password",
        nickname="Test User",
    )