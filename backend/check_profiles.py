"""profiles 테이블 데이터 확인"""

import asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import settings

async def check_profiles():
    """profiles 테이블의 데이터 확인"""
    engine = create_async_engine(settings.DATABASE_URL)

    async with engine.begin() as conn:
        # profiles 테이블의 모든 데이터 조회
        result = await conn.execute(text("SELECT id, email, nickname, created_at FROM profiles ORDER BY created_at DESC LIMIT 10"))
        profiles = result.fetchall()

        print(f"\n=== profiles 테이블 데이터 (최근 10개) ===")
        print(f"총 {len(profiles)}개의 레코드가 있습니다.\n")

        if profiles:
            for profile in profiles:
                print(f"ID: {profile[0]}")
                print(f"Email: {profile[1]}")
                print(f"Nickname: {profile[2]}")
                print(f"Created At: {profile[3]}")
                print("-" * 50)
        else:
            print("profiles 테이블이 비어있습니다.")

        # 특정 이메일로 검색 (사용자가 입력한 이메일로 변경 필요)
        test_email = "user@example.com"  # 여기에 테스트하려는 이메일 입력
        result = await conn.execute(
            text("SELECT * FROM profiles WHERE email = :email"),
            {"email": test_email}
        )
        existing = result.fetchone()

        print(f"\n=== '{test_email}' 이메일 검색 결과 ===")
        if existing:
            print(f"❌ 이메일이 이미 존재합니다: {existing}")
        else:
            print(f"✅ 이메일이 존재하지 않습니다. 회원가입 가능합니다.")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_profiles())
