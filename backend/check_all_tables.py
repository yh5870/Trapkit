"""모든 테이블 상세 확인."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from shared.config.database import get_db


async def check_all_tables():
    """모든 테이블 확인."""
    print("=== Supabase Tables Check ===")

    try:
        async for db in get_db():
            # 모든 테이블 확인
            result = await db.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = result.fetchall()

            print(f"\nTables in database:")
            for (table_name,) in tables:
                print(f"  - {table_name}")

            # 필요한 테이블 확인
            required_tables = ['profiles', 'items', 'memos', 'baggage_rules']
            existing_tables = [name for (name,) in tables]

            print(f"\n=== Required Tables Status ===")
            for table in required_tables:
                status = "[OK] EXISTS" if table in existing_tables else "[MISSING]"
                print(f"{table}: {status}")

            # 누락된 테이블 생성
            missing = [t for t in required_tables if t not in existing_tables]
            if missing:
                print(f"\n=== Creating Missing Tables ===")
                for table in missing:
                    print(f"Creating {table}...")
                    if table == 'items':
                        await db.execute(text("""
                            CREATE TABLE items (
                                id VARCHAR(36) PRIMARY KEY,
                                trip_id VARCHAR(36) NOT NULL,
                                name VARCHAR(255) NOT NULL,
                                item_type VARCHAR(50) NOT NULL,
                                quantity INTEGER DEFAULT 1,
                                weight DECIMAL(10,2),
                                notes TEXT,
                                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                            );
                        """))
                    elif table == 'memos':
                        await db.execute(text("""
                            CREATE TABLE memos (
                                id VARCHAR(36) PRIMARY KEY,
                                item_id VARCHAR(36) NOT NULL,
                                content TEXT NOT NULL,
                                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                            );
                        """))
                    print(f"[OK] {table} created!")

                await db.commit()
            else:
                print(f"\n[OK] All required tables exist!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_all_tables())