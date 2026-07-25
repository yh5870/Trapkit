"""Gemini API 테스트 스크립트.

사용법:
    python test_gemini.py

테스트 내용:
    1. GeminiClient 클래스 직접 테스트 (프로젝트에서 사용하는 방식)
    2. 순수 google.genai 라이브러리 테스트
"""

import asyncio
import os
import sys

# 프로젝트 루트 경로 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# .env 파일 로드
from dotenv import load_dotenv
load_dotenv()

from google import genai

# 프로젝트에서 사용하는 GeminiClient import
from app.application.commands.create_trip import CreateTripCommand
from infrastructure.external.gemini_client import GeminiClient


# ============================================
# 1. 프로젝트 GeminiClient 테스트
# ============================================

async def test_gemini_client_basic():
    """GeminiClient 기본 테스트."""
    print("\n" + "=" * 60)
    print("🚀 GeminiClient 기본 테스트")
    print("=" * 60)

    # 1. GeminiClient 초기화
    print("\n1️⃣ GeminiClient 초기화 중...")
    try:
        client = GeminiClient()
        print("   ✅ 초기화 성공")
        print(f"   - API Key: {client.api_key[:20]}... (masked)")
        print(f"   - Model: {client.model}")
    except Exception as e:
        print(f"   ❌ 초기화 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 2. CreateTripCommand 생성
    print("\n2️⃣ CreateTripCommand 생성 중...")
    command = CreateTripCommand(
        user_id="test_user_123",
        destination="제주도",
        purpose=["관광", "맛집탐방"],
        duration_nights=2,
        departure_month=8,
        companions="가족",
    )
    print("   ✅ Command 생성 성공")
    print(f"   - 여행지: {command.destination}")
    print(f"   - 목적: {', '.join(command.purpose)}")

    # 3. AI 콘텐츠 생성
    print("\n3️⃣ AI 콘텐츠 생성 중...")
    print("   ⏳ API 호출 중... (잠시만 기다려주세요)")

    try:
        content = await client.generate_trip_content(command)
        print("   ✅ AI 생성 성공")
    except Exception as e:
        print(f"   ❌ AI 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 4. 결과 출력
    print("\n4️⃣ 생성된 콘텐츠:")
    print("-" * 60)

    # cautions 출력
    cautions = content.get("cautions", [])
    print(f"\n📝 주의사항 ({len(cautions)}개):")
    for i, caution in enumerate(cautions, 1):
        caution_type = caution.get("type", "알 수 없음")
        message = caution.get("message", "메시지 없음")
        print(f"   {i}. [{caution_type}] {message}")

    # baggage_summary 출력
    baggage = content.get("baggage_summary", [])
    print(f"\n🎒 수화물 요약 ({len(baggage)}개):")
    for i, item in enumerate(baggage, 1):
        category = item.get("category", "알 수 없음")
        count = item.get("count", 0)
        print(f"   {i}. {category}: {count}개")

    print("-" * 60)

    # 5. 캐시 키 확인
    print("\n5️⃣ 캐시 키:")
    cache_key = client._get_cache_key(command)
    print(f"   Key: {cache_key}")

    # 6. 프롬프트 확인
    print("\n6️⃣ 생성된 프롬프트:")
    prompt = client._build_prompt(command)
    print("-" * 60)
    print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
    print("-" * 60)

    print("\n" + "=" * 60)
    print("🎉 기본 테스트 완료!")
    print("=" * 60)

    return True


async def test_gemini_client_cache():
    """GeminiClient 캐시 테스트."""
    print("\n\n" + "=" * 60)
    print("💾 GeminiClient 캐시 테스트")
    print("=" * 60)

    client = GeminiClient()
    command = CreateTripCommand(
        user_id="cache_test_user",
        destination="도쿄",
        purpose=["쇼핑"],
        duration_nights=3,
    )

    # 첫 번째 호출 (캐시 없음)
    print("\n1️⃣ 첫 번째 호출 (캐시 없음)...")
    import time
    start_time = time.time()
    content1 = await client.generate_trip_content(command)
    first_call_time = time.time() - start_time
    print(f"   ✅ 소요 시간: {first_call_time:.2f}초")

    # 두 번째 호출 (캐시 사용)
    print("\n2️⃣ 두 번째 호출 (캐시 사용)...")
    start_time = time.time()
    content2 = await client.generate_trip_content(command)
    second_call_time = time.time() - start_time
    print(f"   ✅ 소요 시간: {second_call_time:.2f}초")

    # 결과 비교
    print("\n3️⃣ 결과 비교:")
    if content1 == content2:
        print("   ✅ 캐시된 데이터가 원본과 일치")
        speedup = first_call_time / second_call_time if second_call_time > 0 else 0
        print(f"   🚀 속도 향상: {speedup:.1f}배 빠름")
    else:
        print("   ⚠️  캐시된 데이터가 원본과 다름")

    print("\n" + "=" * 60)


async def test_gemini_client_multiple():
    """여러 여행지 테스트."""
    print("\n\n" + "=" * 60)
    print("🌍 여러 여행지 테스트")
    print("=" * 60)

    client = GeminiClient()

    test_cases = [
        {
            "destination": "도쿄",
            "purpose": ["쇼핑", "음식"],
            "duration_nights": 3,
            "departure_month": 10,
        },
        {
            "destination": "파리",
            "purpose": ["문화", "사진"],
            "duration_nights": 5,
            "departure_month": 4,
        },
        {
            "destination": "방콕",
            "purpose": ["휴양"],
            "duration_nights": 4,
            "departure_month": 12,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📍 테스트 {i}: {test_case['destination']}")

        command = CreateTripCommand(
            user_id=f"multi_test_user_{i}",
            **test_case
        )

        try:
            content = await client.generate_trip_content(command)
            cautions_count = len(content.get('cautions', []))
            baggage_count = len(content.get('baggage_summary', []))
            print(f"   ✅ 성공 - 주의사항: {cautions_count}개, 수화물: {baggage_count}개")
        except Exception as e:
            print(f"   ❌ 실패: {e}")

    print("\n" + "=" * 60)


# ============================================
# 2. 순수 google.genai 라이브러리 테스트
# ============================================

async def test_simple_chat():
    """간단한 채팅 테스트."""
    print("\n\n" + "=" * 60)
    print("1️⃣ 순수 google.genai: 간단한 채팅 테스트")
    print("=" * 60)

    client = genai.Client()
    prompt = "안녕! 너는 누구야? 한 줄로 소개해줘."

    print(f"\n📝 프롬프트: {prompt}")

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    print(f"✅ 응답: {response.text}")


async def test_json_generation():
    """JSON 응답 테스트."""
    print("\n\n" + "=" * 60)
    print("2️⃣ 순수 google.genai: JSON 생성 테스트")
    print("=" * 60)

    client = genai.Client()

    prompt = """여행 '제주도'에 대한 주의사항과 수화물 리스트를 생성해주세요.
여행 목적: 관광, 맛집 탐방
여행 기간: 3박

다음 JSON 형식으로 응답해주세요:
{
    "cautions": [
        {"type": "weather|health|safety|other", "message": "주의사항 내용"}
    ],
    "baggage_summary": [
        {"category": "clothing|electronics|documents|other", "count": 개수}
    ]
}

JSON만 응답해주세요. 다른 텍스트는 포함하지 마세요."""

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    print(f"✅ 응답:\n{response.text}")

    # JSON 파싱 테스트
    import json
    try:
        parsed = json.loads(response.text)
        print(f"\n🔍 파싱된 JSON:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError as e:
        print(f"\n⚠️  JSON 파싱 실패: {e}")


async def test_config_params():
    """설정 파라미터 테스트."""
    print("\n\n" + "=" * 60)
    print("3️⃣ 순수 google.genai: 설정 파라미터 테스트")
    print("=" * 60)

    client = genai.Client()
    prompt = "한국의 대표적인 음식 3가지만 알려줘."

    print(f"\n📝 프롬프트: {prompt}")

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        max_output_tokens=50,  # 설정 파라미터 직접 전달
        temperature=0.7,
    )

    print(f"✅ 응답 (max_tokens=50, temperature=0.7):")
    print(response.text)


async def test_list_models():
    """사용 가능한 모델 목록 테스트."""
    print("\n\n" + "=" * 60)
    print("4️⃣ 순수 google.genai: 사용 가능한 모델 목록")
    print("=" * 60)

    client = genai.Client()

    try:
        models = client.models.list()
        print("✅ 사용 가능한 모델들 (최대 15개):")
        for i, model in enumerate(models[:15], 1):
            print(f"   {i}. {model.name}")
    except Exception as e:
        print(f"⚠️  모델 목록 조회 실패: {e}")


# ============================================
# 메인 함수
# ============================================

def print_menu():
    """메뉴 출력."""
    print("\n" + "=" * 60)
    print("🤖 Gemini API 테스트 도구")
    print("=" * 60)
    print("1. GeminiClient 기본 테스트 (프로젝트에서 사용하는 방식)")
    print("2. GeminiClient 캐시 테스트")
    print("3. GeminiClient 여러 여행지 테스트")
    print("4. 순수 google.genai: 간단한 채팅 테스트")
    print("5. 순수 google.genai: JSON 생성 테스트")
    print("6. 순수 google.genai: 설정 파라미터 테스트")
    print("7. 순수 google.genai: 모델 목록 테스트")
    print("8. 모든 테스트 실행")
    print("0. 종료")
    print("=" * 60)
    print("\n번호를 입력하세요: ", end="")


async def run_all_tests():
    """모든 테스트 실행."""
    await test_gemini_client_basic()
    await test_gemini_client_cache()
    await test_gemini_client_multiple()
    await test_simple_chat()
    await test_json_generation()
    await test_config_params()
    await test_list_models()


async def main():
    """메인 함수."""
    print("\n🚀 Gemini API 테스트 도구 시작")

    try:
        while True:
            print_menu()
            choice = input().strip()

            if choice == "1":
                await test_gemini_client_basic()
            elif choice == "2":
                await test_gemini_client_cache()
            elif choice == "3":
                await test_gemini_client_multiple()
            elif choice == "4":
                await test_simple_chat()
            elif choice == "5":
                await test_json_generation()
            elif choice == "6":
                await test_config_params()
            elif choice == "7":
                await test_list_models()
            elif choice == "8":
                await run_all_tests()
            elif choice == "0":
                print("\n👋 안녕히 가세요!")
                break
            else:
                print("\n❌ 잘못된 번호입니다. 다시 입력해주세요.")

            if choice != "0":
                print("\n계속하려면 Enter를 누르세요...")
                input()

    except KeyboardInterrupt:
        print("\n\n⏹️  테스트 중단됨")
    except Exception as e:
        print(f"\n\n❌ 테스트 중 에러 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # API 키 확인
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   .env 파일에 GEMINI_API_KEY를 설정해주세요.")
        sys.exit(1)

    asyncio.run(main())