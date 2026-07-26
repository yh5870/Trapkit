"""Supabase 회원가입 테스트 스크립트."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import hash_password
from infrastructure.database.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
from shared.config.database import get_db


async def test_supabase_signup():
    """Supabase 회원가입 기능 테스트."""
    print("Starting Supabase signup test...")

    try:
        async for db in get_db():
            user_repo = SQLAlchemyProfileRepository(db)

            # 이메일 중복 확인
            existing_user = await user_repo.find_by_email("supabase_test@example.com")
            if existing_user:
                print(f"User already exists: {existing_user['id']}")
                return

            # 비밀번호 해시
            password_hash = hash_password("Test1234!")
            print(f"Password hash: {password_hash[:20]}...")

            # 사용자 저장
            try:
                user = await user_repo.save(
                    email="supabase_test@example.com",
                    password_hash=password_hash,
                    nickname="SupabaseTest",
                )
                print(f"SUCCESS: Signup completed!")
                print(f"ID: {user['id']}")
                print(f"Email: {user['email']}")
                print(f"Nickname: {user['nickname']}")
                print(f"Created: {user['created_at']}")
            except Exception as e:
                print(f"ERROR: Signup failed: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_supabase_signup())