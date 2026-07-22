"""테이블 생성 스크립트."""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트 경로를 PYTHONPATH에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 모든 ORM 모델 import (메타데이터에 등록되도록)
import infrastructure.database.models.item_model
import infrastructure.database.models.memo_model
import infrastructure.database.models.profile_model
import infrastructure.database.models.trip_model

from shared.config.database import Base, engine


async def create_tables():
    """모든 테이블 생성."""
    try:
        print("🔄 테이블 생성 시작...")
        print(f"📦 등록된 모델: {list(Base.metadata.tables.keys())}")

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ 테이블 생성 완료!")

        # 생성된 테이블 확인
        async with engine.connect() as conn:
            from sqlalchemy import text
            result = await conn.execute(text("""
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📋 생성된 테이블 ({len(tables)}개):")
            for table in tables:
                print(f"   - {table}")

    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await engine.dispose()

    return True


if __name__ == "__main__":
    success = asyncio.run(create_tables())
    exit(0 if success else 1)
