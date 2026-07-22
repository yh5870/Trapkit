"""DB 연결 테스트."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.config import settings


async def test_db_connection():
    """DB 연결 테스트."""
    try:
        engine = create_async_engine(settings.DATABASE_URL, echo=False)

        print(f"🔗 DB URL: {settings.DATABASE_URL}")
        print("🔄 DB 연결 시도 중...")

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ DB 연결 성공!")
            print(f"📊 PostgreSQL 버전: {version}")

            # 테이블 확인
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 기존 테이블: {tables if tables else '없음'}")

        await engine.dispose()
        return True

    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    exit(0 if success else 1)
