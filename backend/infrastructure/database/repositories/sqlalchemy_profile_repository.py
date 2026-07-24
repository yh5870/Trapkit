"""Profile Repository 구현.

B개발자가 구현한 UserRepository 인터페이스 구현체.
SQLAlchemy를 사용하여 Profile 테이블에 접근.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.user_repository import UserRepository
from infrastructure.database.models.profile_model import ProfileModel


class SQLAlchemyProfileRepository(UserRepository):
    """SQLAlchemy Profile Repository 구현.

    ProfileModel을 사용하여 DB 작업 수행.
    """

    def __init__(self, session: AsyncSession) -> None:
        """초기화.

        Args:
            session: 비동기 DB 세션
        """
        self.session = session

    async def find_by_email(self, email: str) -> dict[str, str] | None:
        """이메일로 사용자 조회."""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.email == email)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_dict(model)

    async def find_by_id(self, user_id: UUID) -> dict[str, str] | None:
        """ID로 사용자 조회."""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.id == str(user_id))
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_dict(model)

    async def save(
        self,
        email: str,
        password_hash: str,
        nickname: str,
    ) -> dict[str, str]:
        """새 사용자 저장."""
        from uuid import uuid4

        model = ProfileModel(
            id=str(uuid4()),  # 랜덤 UUID 생성
            email=email,
            nickname=nickname,
            password_hash=password_hash,
        )

        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)

        return self._to_dict(model)

    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        """비밀번호 변경."""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.id == str(user_id))
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError("User not found")

        model.password_hash = new_password_hash
        await self.session.commit()

    async def soft_delete(self, user_id: UUID) -> None:
        """사용자 soft delete (deleted_at 설정)."""
        result = await self.session.execute(
            select(ProfileModel).where(ProfileModel.id == str(user_id))
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError("User not found")

        # deleted_at 필드가 있으면 설정, 없으면 physical delete
        if hasattr(model, "deleted_at"):
            model.deleted_at = datetime.now(tz=None)
        else:
            await self.session.delete(model)

        await self.session.commit()

    def _to_dict(self, model: ProfileModel) -> dict[str, str]:
        """ORM 모델을 dict로 변환.

        Args:
            model: ProfileModel 인스턴스

        Returns:
            사용자 정보 dict
        """
        return {
            "id": model.id,
            "email": model.email,
            "nickname": model.nickname,
            "password_hash": model.password_hash,
            "created_at": model.created_at.isoformat() if model.created_at else None,
        }