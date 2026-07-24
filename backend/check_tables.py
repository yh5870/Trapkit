"""Supabase 테이블 확인 스크립트."""

import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from shared.config.database import get_db


async def check_tables():
    """데이터베이스 테이블 확인."""
    print("Checking Supabase tables...")

    try:
        async for db in get_db():
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

            # profiles 테이블 확인
            profiles_exists = any(name == 'profiles' for (name,) in tables)
            print(f"\nprofiles table exists: {profiles_exists}")

            if not profiles_exists:
                print("\nCreating profiles table...")
                await db.execute(text("""
                    CREATE TABLE profiles (
                        id VARCHAR(36) PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        nickname VARCHAR(100) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                """))
                await db.commit()
                print("profiles table created!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(check_tables())