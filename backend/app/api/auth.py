"""인증 API (회원가입, 로그인, 로그아웃)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.dependencies import SessionDep
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.utils.logger import setup_logger
from app.utils.exceptions import UnauthorizedException

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: SignupRequest, db: SessionDep):
    """회원가입."""
    # TODO: DB에 사용자 생성
    # user = User(email=body.email, password_hash=hash_password(body.password), nickname=body.nickname)
    # db.add(user)
    # await db.commit()
    # await db.refresh(user)
    logger.info(f"회원가입 요청: {body.email}")

    # 임시 응답
    return UserResponse(
        id="temp-id",
        email=body.email,
        nickname=body.nickname,
        created_at="2026-07-21T00:00:00Z",
    )


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: SessionDep):
    """로그인."""
    # TODO: DB에서 사용자 조회
    # user = await get_user_by_email(db, body.email)
    # if not user or not verify_password(body.password, user.password_hash):
    #     raise UnauthorizedException("이메일 또는 비밀번호가 틀렸습니다.")

    logger.info(f"로그인 요청: {body.email}")

    # 임시 토큰 생성
    token = create_token({"sub": "temp-user-id"})

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=UserResponse(
            id="temp-id",
            email=body.email,
            nickname="여행자",
            created_at="2026-07-21T00:00:00Z",
        ),
    )


@router.post("/logout")
async def logout():
    """로그아웃."""
    # TODO: 토큰 블랙리스트 추가 (선택적)
    logger.info("로그아웃 요청")
    return {"message": "Logged out successfully"}


@router.post("/reset-request")
async def reset_request(email: str):
    """비밀번호 재설정 요청."""
    # TODO: 이메일로 재설정 링크 발송
    logger.info(f"비밀번호 재설정 요청: {email}")
    return {"message": "Reset link sent to email"}


@router.post("/reset")
async def reset_password(token: str, new_password: str):
    """비밀번호 재설정."""
    # TODO: 토큰 검증 및 비밀번호 변경
    logger.info("비밀번호 재설정")
    return {"message": "Password reset successfully"}


@router.delete("/me")
async def delete_account():
    """회원 탈퇴."""
    # TODO: 사용자 soft delete
    # user_id = 인증된 사용자 ID에서 가져오기
    logger.info("회원 탈퇴 요청")
    return {"message": "Account deleted successfully"}