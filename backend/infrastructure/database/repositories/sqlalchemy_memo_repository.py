"""SQLAlchemy Memo Repository Implementation."""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.item import Memo
from app.domain.repositories.memo_repository import MemoRepository
from app.domain.value_objects.memo_id import MemoId
from app.domain.value_objects.trip_id import TripId
from infrastructure.database.models.memo_model import MemoModel


class SQLAlchemyMemoRepository(MemoRepository):
    """MemoRepository의 SQLAlchemy 구현."""

    def __init__(self, session: AsyncSession) -> None:
        """초기화.

        Args:
            session: 비동기 데이터베이스 세션
        """
        self.session = session

    async def save(self, memo: Memo) -> Memo:
        """Memo 저장.

        Args:
            memo: 저장할 Memo 도메인 엔티티

        Returns:
            저장된 Memo 엔티티
        """
        model = self._to_infrastructure(memo)

        # 이미 존재하는지 확인
        existing = await self.session.execute(
            select(MemoModel).where(MemoModel.id == str(memo.id.value))
        )
        existing_model = existing.scalar_one_or_none()
        if existing_model:
            # 업데이트
            existing_model.content = memo.content
            self.session.add(existing_model)
            model = existing_model
        else:
            # 새로 생성
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return self._to_domain(model)

    async def find_by_id(self, memo_id: MemoId) -> Memo | None:
        """ID로 Memo 조회.

        Args:
            memo_id: 조회할 Memo ID

        Returns:
            Memo 엔티티 또는 None
        """
        result = await self.session.execute(
            select(MemoModel).where(MemoModel.id == str(memo_id.value))
        )
        model = result.scalar_one_or_none()

        return self._to_domain(model) if model else None

    async def find_by_trip_id(self, trip_id: TripId) -> list[Memo]:
        """Trip ID로 모든 Memo 조회 (생성일 내림차순).

        Args:
            trip_id: Trip ID

        Returns:
            Memo 엔티티 리스트
        """
        result = await self.session.execute(
            select(MemoModel)
            .where(MemoModel.trip_id == str(trip_id.value))
            .order_by(MemoModel.created_at.desc())
        )
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def delete(self, memo_id: MemoId) -> None:
        """Memo 삭제.

        Args:
            memo_id: 삭제할 Memo ID
        """
        result = await self.session.execute(
            select(MemoModel).where(MemoModel.id == str(memo_id.value))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Memo 삭제 (Trip 삭제 시).

        Args:
            trip_id: Trip ID
        """
        result = await self.session.execute(
            select(MemoModel).where(MemoModel.trip_id == str(trip_id.value))
        )
        models = result.scalars().all()

        for model in models:
            await self.session.delete(model)

        await self.session.commit()

    async def get_count(self, trip_id: TripId) -> int:
        """Trip ID로 Memo 수 조회.

        Args:
            trip_id: Trip ID

        Returns:
            Memo 수
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(MemoModel)
            .where(MemoModel.trip_id == str(trip_id.value))
        )
        count = result.scalar_one()

        return count if count else 0

    def _to_domain(self, model: MemoModel) -> Memo:
        """ORM 모델을 도메인 엔티티로 변환.

        Args:
            model: MemoModel ORM 인스턴스

        Returns:
            Memo 도메인 엔티티
        """
        return Memo(
            id=MemoId(value=UUID(model.id)),
            trip_id=TripId(value=UUID(model.trip_id)),
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_infrastructure(self, memo: Memo) -> MemoModel:
        """도메인 엔티티를 ORM 모델로 변환.

        Args:
            memo: Memo 도메인 엔티티

        Returns:
            MemoModel ORM 인스턴스
        """
        return MemoModel(
            id=str(memo.id.value),
            trip_id=str(memo.trip_id.value),
            content=memo.content,
        )