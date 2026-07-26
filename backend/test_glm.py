"""GLM Client Test (GLM 전용).

사용법:
    python test_glm.py

테스트 내용:
    1. GLMClient 기본 테스트
    2. 아이템 생성 확인
"""

import asyncio
import sys

from app.config import settings
from app.application.commands.create_trip import CreateTripCommand
from infrastructure.external.glm_client import GLMClient


async def main():
    print("=" * 60)
    print("GLM Client Test (GLM 전용)")
    print("=" * 60)
    print()

    # 1. Settings check
    print("1. Checking settings...")
    print(f"   GLM API Key: {settings.GLM_API_KEY[:20]}... (masked)")
    print(f"   GLM Model: {settings.GLM_MODEL}")
    print(f"   AI Max Tokens: {settings.AI_MAX_TOKENS}")
    print()

    # 2. Initialize client
    print("2. Initializing GLMClient...")
    try:
        client = GLMClient()
        print("   [OK] Init successful")
        print(f"   - API Key: {client.api_key[:20]}... (masked)")
        print(f"   - Model: {client.model}")
        print()
    except Exception as e:
        print(f"   [FAIL] Init failed: {e}")
        sys.exit(1)

    # 3. Create command
    print("3. Creating CreateTripCommand...")
    command = CreateTripCommand(
        user_id="test-user",
        destination="제주도",
        purpose=["관광", "맛집탐방"],
        duration_nights=3,
        departure_month=8,
        companions="가족",
    )
    print(f"   [OK] Command created")
    print(f"   - Destination: {command.destination}")
    print(f"   - Purpose: {', '.join(command.purpose)}")
    print()

    # 4. AI content generation
    print("4. Generating AI content...")
    print("   [WAIT] Calling API... (please wait)")
    print()

    try:
        content = await client.generate_trip_content(command)
        print("   [OK] AI generation successful!")
        print()
        print("Results:")
        print()

        # cautions
        print("   📝 주의사항:")
        cautions = content.get('cautions', [])
        if cautions:
            for caution in cautions:
                print(f"      * [{caution.get('type', 'unknown')}] {caution.get('message', '')}")
        else:
            print("      * 없음")
        print()

        # items (체크리스트)
        print("   🎒 체크리스트 아이템:")
        items = content.get('items', [])
        if items:
            for i, item in enumerate(items, 1):
                category = item.get('category', 'unknown')
                name = item.get('name', 'unknown')
                quantity = item.get('quantity', 1)
                tip = item.get('tip')
                baggage_flag = item.get('baggage_flag', False)

                print(f"      {i}. [{category}] {name} x{quantity}")
                if tip:
                    print(f"         💡 {tip}")
                if baggage_flag:
                    print(f"         ⚠️ 수화물 규정 체크 필요")
        else:
            print("      * 없음")
        print()

        # baggage_summary
        print("   📊 수화물 요약:")
        baggage = content.get('baggage_summary', [])
        if baggage:
            for item in baggage:
                print(f"      * [{item.get('category', 'unknown')}] {item.get('count', 0)}개")
        else:
            print("      * 없음")
        print()

        print(f"   ✅ 총 아이템 수: {len(items)}개")
        print(f"   ✅ 총 주의사항 수: {len(cautions)}개")
        print()
    except Exception as e:
        print(f"   [FAIL] AI generation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())