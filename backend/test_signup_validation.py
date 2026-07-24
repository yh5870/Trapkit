"""회원가입 유효성 검증 테스트"""

from app.schemas.auth import SignupRequest, LoginRequest
from pydantic import ValidationError

def test_signup_validations():
    """회원가입 유효성 검증 테스트"""

    print("=== 회원가입 유효성 검증 테스트 ===\n")

    # 테스트 케이스들
    test_cases = [
        {
            "name": "유효한 데이터",
            "data": {
                "email": "newuser@example.com",
                "password": "password123",  # 영문+숫자 조합, 8자 이상
                "nickname": "테스트유저"
            },
            "should_pass": True
        },
        {
            "name": "비밀번호 7자 (너무 짧음)",
            "data": {
                "email": "newuser2@example.com",
                "password": "pass123",  # 7자
                "nickname": "테스트"
            },
            "should_pass": False
        },
        {
            "name": "비밀번호 영문만 (숫자 없음)",
            "data": {
                "email": "newuser3@example.com",
                "password": "password",  # 영문만
                "nickname": "테스트"
            },
            "should_pass": False
        },
        {
            "name": "비밀번호 숫자만 (영문 없음)",
            "data": {
                "email": "newuser4@example.com",
                "password": "12345678",  # 숫자만
                "nickname": "테스트"
            },
            "should_pass": False
        },
        {
            "name": "닉네임 빈 문자열",
            "data": {
                "email": "newuser5@example.com",
                "password": "password123",
                "nickname": ""  # 빈 문자열
            },
            "should_pass": False
        },
        {
            "name": "유효하지 않은 이메일",
            "data": {
                "email": "invalid-email",
                "password": "password123",
                "nickname": "테스트"
            },
            "should_pass": False
        },
        {
            "name": "비밀번호 101자 (너무 김)",
            "data": {
                "email": "newuser6@example.com",
                "password": "a" * 101,
                "nickname": "테스트"
            },
            "should_pass": False
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   데이터: {test_case['data']}")

        try:
            SignupRequest(**test_case['data'])
            if test_case['should_pass']:
                print("   ✅ 통과 (예상대로)")
            else:
                print("   ❌ 실패 예상이었으나 통과함")
        except ValidationError as e:
            if not test_case['should_pass']:
                print("   ✅ 실패 (예상대로)")
                print(f"   에러: {e.errors()[0]['msg']}")
            else:
                print("   ❌ 통과 예상이었으나 실패함")
                print(f"   에러: {e}")
        print()

if __name__ == "__main__":
    test_signup_validations()
