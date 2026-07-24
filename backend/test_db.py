"""DB 연결 테스트."""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from shared.config.database import get_db, engine
from sqlalchemy import text


async def test_db_connection():
    """DB 연결 테스트."""
    print("🔍 DB 연결 테스트 시작...")

    try:
        # Engine 테스트
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            print(f"✅ Engine 연결 성공: {result.fetchone()}")

        # Session 테스트
        async with get_db() as session:
            result = await session.execute(text("SELECT NOW()"))
            print(f"✅ Session 연결 성공: {result.fetchone()}")

            # profiles 테이블 확인
            result = await session.execute(text("SELECT COUNT(*) FROM profiles"))
            count = result.fetchone()[0]
            print(f"✅ profiles 테이블 확인: {count}개 레코드")

    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        import traceback
        traceback.print_exc()


async def test_repository():
    """Repository 테스트."""
    print("\n🔍 Repository 테스트 시작...")

    try:
        from infrastructure.database.dependencies.repositories import get_user_repository
        from app.domain.repositories.user_repository import UserRepository

        # 세션 생성
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        from app.config import settings

        engine = create_async_engine(settings.DATABASE_URL, echo=True)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        async with async_session() as session:
            # Repository 테스트
            user_repo = get_user_repository(session)

            # 이메일 조회 테스트
            user = await user_repo.find_by_email("test@example.com")
            print(f"✅ find_by_email 테스트: {user}")

            # 저장 테스트
            user = await user_repo.save(
                email="test@example.com",
                password_hash="test_hash",
                nickname="테스트유저",
            )
            print(f"✅ save 테스트: {user}")

    except Exception as e:
        print(f"❌ Repository 테스트 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_db_connection())
    asyncio.run(test_repository())