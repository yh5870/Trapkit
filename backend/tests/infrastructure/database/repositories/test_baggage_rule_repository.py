"""Baggage Repository 테스트."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import select

from app.domain.repositories.baggage_rule_repository import BaggageRuleRepository
from infrastructure.database.models.baggage_rule_model import BaggageRuleModel
from infrastructure.database.repositories.sqlalchemy_baggage_rule_repository import SQLAlchemyBaggageRuleRepository
from shared.config.database import Base
from tests.conftest import async_session_maker, engine

# 테스트용 DB URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_trapkit"


@pytest.fixture
async def test_session():
    """테스트용 비동기 세션."""
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession
    )
    async with async_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_find_by_key_existing(test_session: AsyncSession):
    """존재하는 키로 규칙 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    # 테스트용 데이터 삽입
    rule = BaggageRuleModel(
        item_key="test_laptop",
        display_name="테스트 노트북",
        aliases=["test", "노트북"],
        unit="개",
        carry_on_rule={"max_size_cm": 35.5, "condition": "기내용 가능"},
        checked_rule={"condition": "위탁 가능"},
        tips="테스트 팁",
        source="test"
    )
    test_session.add(rule)
    await test_session.commit()

    # 조회 테스트
    result = await repo.find_by_key("test_laptop")

    assert result is not None
    assert result["item_key"] == "test_laptop"
    assert result["display_name"] == "테스트 노트북"
    assert "test" in result["aliases"]

    # 정리
    await test_session.delete(rule)


@pytest.mark.asyncio
async def test_find_by_key_not_existing(test_session: AsyncSession):
    """존재하지 않는 키로 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    result = await repo.find_by_key("not_existing_item")

    assert result is None


@pytest.mark.asyncio
async def test_find_by_normalized_key_exact_match(test_session: AsyncSession):
    """정규화된 키로 정확히 일치하는 규칙 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    # 테스트용 데이터 삽입
    rule = BaggageRuleModel(
        item_key="power_bank",
        display_name="보조배터리",
        aliases=["power bank", "배터리", "충전기"],
        unit="개",
        carry_on_rule={"max_wh": 100, "condition": "100Wh 이하만 기내 가능"},
        checked_rule={"max_wh": 160, "condition": "160Wh 이하만 위탁 가능"},
        tips="테스트 팁",
        source="test"
    )
    test_session.add(rule)
    await test_session.commit()

    # 정확히 일치
    result = await repo.find_by_normalized_key("power_bank")
    assert result is not None
    assert result["item_key"] == "power_bank"

    # 별칭 매칭 (소문자 무시)
    result2 = await repo.find_by_normalized_key("powerbank")
    assert result2 is not None
    assert result2["item_key"] == "power_bank"

    # 정리
    await test_session.delete(rule)


@pytest.mark.asyncio
async def test_find_by_normalized_key_alias_match(test_session: AsyncSession):
    """별칭으로 규칙 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    # 테스트용 데이터 삽입
    rule = BaggageRuleModel(
        item_key="smartphone",
        display_name="스마트폰",
        aliases=["smartphone", "폰", "phone", "갤럭시S", "iphone"],
        unit="개",
        carry_on_rule={"condition": "기내 휴대 가능"},
        checked_rule={"condition": "위탁 가능"},
        tips="테스트 팁",
        source="test"
    )
    test_session.add(rule)
    await test_session.commit()

    # 별칭 매칭
    result = await repo.find_by_normalized_key("iphone")
    assert result is not None
    assert result["item_key"] == "smartphone"

    # 정리
    await test_session.delete(rule)


@pytest.mark.asyncio
async def test_get_all_rules(test_session: AsyncSession):
    """모든 규칙 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    # 테스트용 데이터 삽입 (2개)
    rule1 = BaggageRuleModel(
        item_key="test_item_1",
        display_name="테스트 아이템 1",
        aliases=["test1"],
        unit="개",
        carry_on_rule={"condition": "기내용 가능"},
        checked_rule={"condition": "위탁 가능"},
        tips="테스트 팁",
        source="test"
    )
    rule2 = BaggageRuleModel(
        item_key="test_item_2",
        display_name="테스트 아이템 2",
        aliases=["test2"],
        unit="개",
        carry_on_rule={"condition": "기내용 가능"},
        checked_rule={"condition": "위탁 가능"},
        tips="테스트 팁",
        source="test"
    )
    test_session.add_all([rule1, rule2])
    await test_session.commit()

    # 모든 규칙 조회
    result = await repo.get_all_rules()

    assert len(result) >= 2
    item_keys = {r["item_key"] for r in result}
    assert "test_item_1" in item_keys
    assert "test_item_2" in item_keys

    # 정리
    await test_session.delete(rule1)
    await test_session.delete(rule2)


@pytest.mark.asyncio
async def test_get_all_rules_empty(test_session: AsyncSession):
    """빈 데이터베이스에서 모든 규칙 조회."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    result = await repo.get_all_rules()

    # 빈 목록이어야 함
    assert isinstance(result, list)
    # 빈 리스트일 수도 []이 나와야 함
    assert len(result) == 0 or result == []


@pytest.mark.asyncio
async def test_repository_dependency_injection(test_client, test_session: AsyncSession):
    """의존성 주입 테스트."""
    from infrastructure.database.dependencies.repositories import get_baggage_rule_repository

    repo = get_baggage_rule_repository(test_session)

    assert repo is not None
    assert isinstance(repo, SQLAlchemyBaggageRuleRepository)


@pytest.mark.asyncio
async def test_to_dict_method(test_session: AsyncSession):
    """to_dict 메서드 테스트."""
    rule = BaggageRuleModel(
        item_key="test_dict",
        display_name="테스트 딕셔너리",
        aliases=["test"],
        unit="개",
        carry_on_rule={"condition": "기내용 가능"},
        checked_rule={"condition": "위탁 가능"},
        tips="테스트 팁",
        source="test"
    )

    result = rule.to_dict()

    assert result["item_key"] == "test_dict"
    assert result["display_name"] == "테스트 딕셔너리"
    assert isinstance(result["aliases"], list)
    assert isinstance(result["carry_on_rule"], dict)
    assert isinstance(result["checked_rule"], dict)