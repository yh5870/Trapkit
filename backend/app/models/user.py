"""User 모델."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class User:
    """User 모델 (SQLAlchemy)."""

    # TODO: 실제 SQLAlchemy Base 상속 모델로 변경
    # class User(Base):
    #     __tablename__ = "users"
    #
    #     id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    #     email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    #     password_hash: Mapped[str] = mapped_column(String(255))
    #     nickname: Mapped[str] = mapped_column(String(100))
    #     created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    #     deleted_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # 임시 스텁
    def __init__(self, id: str, email: str, password_hash: str, nickname: str) -> None:
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.nickname = nickname