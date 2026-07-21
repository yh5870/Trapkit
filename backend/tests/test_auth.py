"""인증 API 테스트."""

from fastapi import status


async def test_health_check(client):
    """헬스체크 테스트."""
    response = await client.get("/health/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"


async def test_signup(client):
    """회원가입 테스트."""
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": "newuser@example.com",
            "password": "Password123",
            "nickname": "새 여행자",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["nickname"] == "새 여행자"


async def test_login(client):
    """로그인 테스트."""
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "user@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"


async def test_logout(client):
    """로그아웃 테스트."""
    response = await client.post("/api/auth/logout")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logged out successfully"


async def test_signup_invalid_password(client):
    """비밀번호 규칙 실패 테스트."""
    response = await client.post(
        "/api/auth/signup",
        json={
            "email": "user@example.com",
            "password": "short",  # 8자 미만
            "nickname": "User",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY