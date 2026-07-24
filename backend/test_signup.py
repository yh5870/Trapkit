"""회원가입 테스트 스크립트."""

import asyncio
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from app.core.security import hash_password
from infrastructure.database.repositories.sqlalchemy_profile_repository import SQLAlchemyProfileRepository
from shared.config.database import get_db


async def test_signup():
    """회원가입 기능 테스트."""
    async for db in get_db():
        user_repo = SQLAlchemyProfileRepository(db)

        # 이메일 중복 확인
        existing_user = await user_repo.find_by_email("testuser@example.com")
        if existing_user:
            print(f"이미 존재하는 사용자: {existing_user}")
            return

        # 비밀번호 해시
        password_hash = hash_password("Test1234!")
        print(f"비밀번호 해시: {password_hash[:20]}...")

        # 사용자 저장
        try:
            user = await user_repo.save(
                email="testuser@example.com",
                password_hash=password_hash,
                nickname="TestUser",
            )
            print("SUCCESS: 회원가입 성공!")
            print(f"ID: {user['id']}")
            print(f"Email: {user['email']}")
            print(f"Nickname: {user['nickname']}")
            print(f"Created: {user['created_at']}")
        except Exception as e:
            print(f"ERROR: 회원가입 실패: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_signup())