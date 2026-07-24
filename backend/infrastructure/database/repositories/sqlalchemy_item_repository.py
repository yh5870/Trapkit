"""SQLAlchemy Item Repository Implementation."""

from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.item import Item
from app.domain.repositories.item_repository import ItemRepository
from app.domain.value_objects.item_id import ItemId
from app.domain.value_objects.trip_id import TripId
from infrastructure.database.models.item_model import ItemModel


class SQLAlchemyItemRepository(ItemRepository):
    """ItemRepository의 SQLAlchemy 구현."""

    def __init__(self, session: AsyncSession) -> None:
        """초기화.

        Args:
            session: 비동기 데이터베이스 세션
        """
        self.session = session

    async def save(self, item: Item) -> Item:
        """Item 저장.

        Args:
            item: 저장할 Item 도메인 엔티티

        Returns:
            저장된 Item 엔티티
        """
        model = self._to_infrastructure(item)

        # 이미 존재하는지 확인
        existing = await self.session.execute(
            select(ItemModel).where(ItemModel.id == str(item.id.value))
        )
        existing_model = existing.scalar_one_or_none()
        if existing_model:
            # 업데이트
            existing_model.category = item.category
            existing_model.name = item.name
            existing_model.quantity = item.quantity
            existing_model.tip = item.tip
            existing_model.baggage_flag = item.baggage_flag
            existing_model.source = item.source
            existing_model.checked = item.checked
            existing_model.sort_order = item.sort_order
            self.session.add(existing_model)
            model = existing_model
        else:
            # 새로 생성
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return self._to_domain(model)

    async def find_by_id(self, item_id: ItemId) -> Item | None:
        """ID로 Item 조회.

        Args:
            item_id: 조회할 Item ID

        Returns:
            Item 엔티티 또는 None
        """
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == str(item_id.value))
        )
        model = result.scalar_one_or_none()

        return self._to_domain(model) if model else None

    async def find_by_trip_id(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (생성일 내림차순).

        Args:
            trip_id: Trip ID

        Returns:
            Item 엔티티 리스트
        """
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.trip_id == str(trip_id.value))
            .order_by(ItemModel.created_at.desc())
        )
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def find_by_trip_id_sorted(self, trip_id: TripId) -> list[Item]:
        """Trip ID로 모든 Item 조회 (sort_order 오름차순).

        Args:
            trip_id: Trip ID

        Returns:
            Item 엔티티 리스트
        """
        result = await self.session.execute(
            select(ItemModel)
            .where(ItemModel.trip_id == str(trip_id.value))
            .order_by(ItemModel.sort_order.asc())
        )
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def find_by_category(
        self,
        trip_id: TripId,
        category: str
    ) -> list[Item]:
        """Trip ID와 카테고리로 Item 조회.

        Args:
            trip_id: Trip ID
            category: 카테고리

        Returns:
            Item 엔티티 리스트
        """
        result = await self.session.execute(
            select(ItemModel)
            .where(
                ItemModel.trip_id == str(trip_id.value),
                ItemModel.category == category
            )
            .order_by(ItemModel.created_at.desc())
        )
        models = result.scalars().all()

        return [self._to_domain(model) for model in models]

    async def delete(self, item_id: ItemId) -> None:
        """Item 삭제.

        Args:
            item_id: 삭제할 Item ID
        """
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == str(item_id.value))
        )
        model = result.scalar_one_or_none()

        if model:
            await self.session.delete(model)
            await self.session.commit()

    async def delete_by_trip_id(self, trip_id: TripId) -> None:
        """Trip ID로 모든 Item 삭제 (Trip 삭제 시).

        Args:
            trip_id: Trip ID
        """
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.trip_id == str(trip_id.value))
        )
        models = result.scalars().all()

        for model in models:
            await self.session.delete(model)

        await self.session.commit()

    async def get_checked_count(self, trip_id: TripId) -> int:
        """Trip ID로 완료된 Item 수 조회.

        Args:
            trip_id: Trip ID

        Returns:
            완료된 Item 수
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(ItemModel)
            .where(
                ItemModel.trip_id == str(trip_id.value),
                ItemModel.checked == True
            )
        )
        count = result.scalar_one()

        return count if count else 0

    async def get_total_count(self, trip_id: TripId) -> int:
        """Trip ID로 전체 Item 수 조회.

        Args:
            trip_id: Trip ID

        Returns:
            전체 Item 수
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(ItemModel)
            .where(ItemModel.trip_id == str(trip_id.value))
        )
        count = result.scalar_one()

        return count if count else 0

    async def update_sort_order(
        self,
        item_id: ItemId,
        new_order: int
    ) -> None:
        """Item 정렬 순서 업데이트.

        Args:
            item_id: Item ID
            new_order: 새로운 정렬 순서
        """
        result = await self.session.execute(
            select(ItemModel).where(ItemModel.id == str(item_id.value))
        )
        model = result.scalar_one_or_none()

        if model:
            model.sort_order = new_order
            await self.session.commit()
            await self.session.refresh(model)

    def _to_domain(self, model: ItemModel) -> Item:
        """ORM 모델을 도메인 엔티티로 변환.

        Args:
            model: ItemModel ORM 인스턴스

        Returns:
            Item 도메인 엔티티
        """
        return Item(
            id=ItemId(value=UUID(model.id)),
            trip_id=TripId(value=UUID(model.trip_id)),
            category=model.category,
            name=model.name,
            quantity=model.quantity,
            tip=model.tip,
            baggage_flag=model.baggage_flag,
            source=model.source,
            checked=model.checked,
            sort_order=model.sort_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_infrastructure(self, item: Item) -> ItemModel:
        """도메인 엔티티를 ORM 모델로 변환.

        Args:
            item: Item 도메인 엔티티

        Returns:
            ItemModel ORM 인스턴스
        """
        return ItemModel(
            id=str(item.id.value),
            trip_id=str(item.trip_id.value),
            category=item.category,
            name=item.name,
            quantity=item.quantity,
            tip=item.tip,
            baggage_flag=item.baggage_flag,
            source=item.source,
            checked=item.checked,
            sort_order=item.sort_order,
        )
