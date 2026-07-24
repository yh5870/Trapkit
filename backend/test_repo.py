"""Repository 직접 테스트."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.database.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings


async def test():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        repo = SQLAlchemyProfileRepository(session)

        # 저장 테스트
        user = await repo.save(
            email="test@example.com",
            password_hash="test_hash",
            nickname="테스트유저",
        )
        print(f"✅ 저장 성공: {user}")

        # 조회 테스트
        user = await repo.find_by_email("test@example.com")
        print(f"✅ 조회 성공: {user}")


if __name__ == "__main__":
    asyncio.run(test())