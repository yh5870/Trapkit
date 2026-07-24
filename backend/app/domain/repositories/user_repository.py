"""User Repository 인터페이스.

A개발자가 정의한 도메인 인터페이스.
B개발자는 SQLAlchemy로 구현.
"""

from abc import ABC, abstractmethod
from uuid import UUID

from pydantic import EmailStr


class UserRepository(ABC):
    """User Repository 인터페이스.

    Supabase Auth의 auth.users 테이블과 연동되는 사용자 데이터 접근 계층입니다.
    """

    @abstractmethod
    async def find_by_email(self, email: str) -> dict[str, str] | None:
        """이메일로 사용자 조회.

        Args:
            email: 사용자 이메일

        Returns:
            사용자 정보 dict (id, email, nickname, password_hash) 또는 None
        """
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> dict[str, str] | None:
        """ID로 사용자 조회.

        Args:
            user_id: 사용자 UUID

        Returns:
            사용자 정보 dict (id, email, nickname) 또는 None
        """
        pass

    @abstractmethod
    async def save(
        self,
        email: str,
        password_hash: str,
        nickname: str,
    ) -> dict[str, str]:
        """새 사용자 저장.

        Args:
            email: 사용자 이메일
            password_hash: 비밀번호 해시
            nickname: 사용자 닉네임

        Returns:
            저장된 사용자 정보 dict (id, email, nickname, created_at)
        """
        pass

    @abstractmethod
    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        """비밀번호 변경.

        Args:
            user_id: 사용자 UUID
            new_password_hash: 새 비밀번호 해시
        """
        pass

    @abstractmethod
    async def soft_delete(self, user_id: UUID) -> None:
        """사용자 soft delete (deleted_at 설정).

        Args:
            user_id: 사용자 UUID
        """
        pass