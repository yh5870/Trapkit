"""인증 API (회원가입, 로그인, 로그아웃)."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.dependencies import SessionDep
from app.domain.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.utils.logger import setup_logger
from app.utils.exceptions import UnauthorizedException
from infrastructure.database.dependencies import get_user_repository
from interfaces.api.dependencies.auth import get_current_user_id

logger = setup_logger(__name__)
router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: SignupRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """회원가입."""
    logger.info(f"회원가입 요청: {body.email}")

    # 이메일 중복 확인
    existing_user = await user_repo.find_by_email(body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다.",
        )

    # 비밀번호 해시
    password_hash = hash_password(body.password)

    # 사용자 저장
    user = await user_repo.save(
        email=body.email,
        password_hash=password_hash,
        nickname=body.nickname,
    )

    logger.info(f"회원가입 완료: {body.email}, ID: {user['id']}")

    return UserResponse(
        id=user["id"],
        email=user["email"],
        nickname=user["nickname"],
        created_at=user["created_at"] or "",
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    user_repo: UserRepository = Depends(get_user_repository),
):
    """로그인."""
    logger.info(f"로그인 요청: {body.email}")

    # 사용자 조회
    user = await user_repo.find_by_email(body.email)

    # 사용자 없거나 비밀번호 불일치
    if not user or not verify_password(body.password, user["password_hash"]):
        raise UnauthorizedException("이메일 또는 비밀번호가 틀렸습니다.")

    # JWT 토큰 생성
    token = create_token({"sub": user["id"], "email": user["email"]})

    logger.info(f"로그인 성공: {body.email}")

    return TokenResponse(
        access_token=token,
        token_type="Bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            nickname=user["nickname"],
            created_at=user["created_at"] or "",
        ),
    )


@router.post("/logout")
async def logout():
    """로그아웃."""
    # TODO: 토큰 블랙리스트 추가 (선택적)
    logger.info("로그아웃 요청")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """현재 사용자 정보 조회."""
    logger.info(f"사용자 정보 조회: {user_id}")

    from uuid import UUID

    user = await user_repo.find_by_id(UUID(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )

    return UserResponse(
        id=user["id"],
        email=user["email"],
        nickname=user["nickname"],
        created_at=user["created_at"] or "",
    )


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
async def delete_account(
    user_id: str = Depends(get_current_user_id),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """회원 탈퇴."""
    logger.info(f"회원 탈퇴 요청: {user_id}")

    from uuid import UUID

    try:
        await user_repo.soft_delete(UUID(user_id))
        logger.info(f"회원 탈퇴 완료: {user_id}")
        return {"message": "Account deleted successfully"}
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다.",
        )