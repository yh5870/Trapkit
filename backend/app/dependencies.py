"""의존성 주입 (DB 세션, 인증)."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token
from app.models.user import User

# DB 세션 의존성
SessionDep = Annotated[AsyncSession, Depends(get_db)]

# HTTP Bearer 인증
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: SessionDep,
) -> User:
    """현재 인증된 사용자 반환."""
    try:
        token = credentials.credentials
        user_id = verify_token(token)

        # TODO: DB에서 user 조회
        # user = await get_user_by_id(db, user_id)
        # if not user:
        #     raise HTTPException(status_code=401, detail="Invalid token")

        # 임시: User 객체 반환
        return User(id=user_id, email="user@example.com", password_hash="", nickname="User")

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: SessionDep,
) -> User | None:
    """현재 인증된 사용자 반환 (선택적)."""
    try:
        token = credentials.credentials
        user_id = verify_token(token)
        return User(id=user_id, email="user@example.com", password_hash="", nickname="User")
    except Exception:
        return None


UserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[User | None, Depends(get_current_user_optional)]