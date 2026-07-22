"""Profile ORM Model."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from shared.config.database import Base


class ProfileModel(Base):
    """Profile 테이블 ORM 모델.

    Supabase Auth의 auth.users 테이블과 연동되는 사용자 프로필 정보입니다.
    """

    __tablename__ = "profiles"

    # Primary Key (auth.users.id와 동일)
    id: Mapped[UUID] = mapped_column(
        String(36),
        primary_key=True,
        index=True,
    )

    # Basic Fields
    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # trips = relationship("TripModel", back_populates="user", cascade="all, delete-orphan")
