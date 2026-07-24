"""Gemini API 간단 테스트 스크립트 (google.genai 사용).

사용법:
    python test_gemini.py
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


async def test_simple_chat():
    """간단한 채팅 테스트."""
    print("\n" + "="*50)
    print("1️⃣ 간단한 채팅 테스트")
    print("="*50)

    client = genai.Client()
    prompt = "안녕! 너는 누구야? 한 줄로 소개해줘."

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    print(f"\n📝 프롬프트: {prompt}")
    print(f"✅ 응답: {response.text}")


async def test_json_generation():
    """JSON 응답 테스트."""
    print("\n" + "="*50)
    print("2️⃣ JSON 생성 테스트")
    print("="*50)

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
    print(f"\n📝 프롬프트: {prompt[:50]}...")
    print(f"✅ 응답:\n{response.text}")

    # JSON 파싱 테스트
    import json
    try:
        parsed = json.loads(response.text)
        print(f"\n🔍 파싱된 JSON:")
        print(json.dumps(parsed, indent=2, ensure_ascii=False))
    except json.JSONDecodeError:
        print("\n⚠️  JSON 파싱 실패")


async def test_streaming():
    """스트리밍 테스트."""
    print("\n" + "="*50)
    print("3️⃣ 스트리밍 테스트")
    print("="*50)

    client = genai.Client()
    prompt = "파이썬이 무엇인지 3문장으로 설명해줘."

    print(f"\n📝 프롬프트: {prompt}")
    print("✅ 응답:")

    response = await client.aio.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )
    print(response.text)


async def test_list_models():
    """사용 가능한 모델 목록 테스트."""
    print("\n" + "="*50)
    print("4️⃣ 사용 가능한 모델 목록")
    print("="*50)

    client = genai.Client()

    try:
        models = client.models.list()
        print("✅ 사용 가능한 모델들 (최대 15개):")
        for model in models:
            print(f"   - {model.name}")
    except Exception as e:
        print(f"⚠️  모델 목록 조회 실패: {e}")


async def main():
    """메인 테스트 실행."""
    print("\n🚀 Gemini API 테스트 시작 (google.genai)")

    try:
        # 먼저 모델 목록 확인
        await test_list_models()

        # 기본 테스트
        await test_simple_chat()
        await test_json_generation()
        await test_streaming()

        print("\n" + "="*50)
        print("✅ 모든 테스트 완료!")
        print("="*50)

    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
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