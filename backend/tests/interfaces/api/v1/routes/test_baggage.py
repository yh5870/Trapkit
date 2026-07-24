"""Baggage API 테스트."""

import pytest
from unittest.mock import AsyncMock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.domain.services.baggage_service import BaggageService
from app.domain.value_objects.verdict import Verdict, VerdictType
from app.main import app
from tests.conftest import async_session_maker, engine
from tests.infrastructure.database.repositories.test_baggage_rule_repository import test_session
from infrastructure.database.models.baggage_rule_model import BaggageRuleModel
from infrastructure.database.repositories.sqlalchemy_baggage_rule_repository import SQLAlchemyBaggageRuleRepository
from shared.config.database import Base
from app.domain.repositories.baggage_rule_repository import BaggageRuleRepository
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# 테스트용 DB URL
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_trapkit"


@pytest.fixture
def client():
    """테스트용 FastAPI 클라이언트."""
    return TestClient(app)


@pytest.fixture
async def test_session_with_data(test_session):
    """테스트용 데이터가 포함된 세션."""
    repo = SQLAlchemyBaggageRuleRepository(test_session)

    # 테스트용 데이터 삽입 (2개)
    rule1 = BaggageRuleModel(
        item_key="laptop",
        display_name="노트북",
        aliases=["laptop", "맥북", "notebook"],
        unit="개",
        carry_on_rule={
            "max_size_cm": 35.5,
            "max_wh": None,
            "condition": "기내용 16x9x9인치 이내 가능 (약 40x23x23cm)",
        },
        checked_rule={
            "max_size": None,
            "max_wh": None,
            "condition": "전자기기로 위탁 가능",
        },
        tips="보안 검색 대기 시간 단축을 위해 파워 코드를 분리해서 제출",
        source="iata"
    )

    rule2 = BaggageRuleModel(
        item_key="power_bank",
        display_name="보조배터리",
        aliases=["power bank", "배터리", "충전기"],
        unit="개",
        carry_on_rule={
            "max_wh": 100,
            "condition": "100Wh 이하만 기내 휴대 가능 (리튬이온 배터리 기준)",
        },
        checked_rule={
            "max_wh": 160,
            "condition": "160Wh 이하만 위탁 가능 (리튬이온 배터리 기준)",
        },
        tips="배터리 용량은 제품 라벨에 표시된 Wh(와트시)를 확인 (mAh ÷ 전압 × 3.7 = Wh)",
        source="iata"
    )

    test_session.add_all([rule1, rule2])
    await test_session.commit()

    return test_session


@pytest.mark.asyncio
async def test_baggage_check_laptop_normal(client, test_session_with_data, monkeypatch):
    """노트북 정상 체크 테스트."""
    # BaggageService 모킹
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    # monkeypatch로 의존성 주입
    app.dependency_overrides[BaggageService] = get_baggage_service

    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
            "value": 15.6,
            "unit": "inch"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 응답 구조 검증
    assert "carry_on" in data
    assert "checked" in data
    assert "carry_on_verdict" not in data  # 예전 필드 제거

    # 판정 결과 검증
    assert data["carry_on"]["verdict"] in ["allowed", "conditional", "forbidden"]
    assert data["checked"]["verdict"] in ["allowed", "conditional", "forbidden"]
    assert data["carry_on"]["label"]  # 라벨 존재
    assert data["carry_on"]["emoji"]  # 이모지 존재
    assert isinstance(data["carry_on"]["is_allowed"], bool)
    assert isinstance(data["carry_on"]["is_forbidden"], bool)


@pytest.mark.asyncio
async def test_baggage_check_power_bank_normal(client, test_session_with_data, monkeypatch):
    """보조배터리 정상 체크 테스트."""
    # BaggageService 모킹
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "보조배터리",
            "value": 80.0,
            "unit": "wh"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 보조배터리 규칙 (100Wh 이하 기내 가능, 160Wh 이하 위탁 가능)
    assert data["carry_on"]["verdict"] == "allowed"
    assert data["carry_on"]["reason"] == "기내 반입 가능: 80.0wh"
    assert data["checked"]["verdict"] == "allowed"
    assert data["checked"]["reason"] == "위탁 반입 가능: 80.0wh"


@pytest.mark.asyncio
async def test_baggage_check_unauthorized(client):
    """인증 없는 요청 처리 테스트."""
    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
            "value": 15.6,
            "unit": "inch"
        }
    )

    # 인증 없으면 401 또는 403 (FastAPI 기본 동작)
    assert response.status_code in [401, 403]


@pytest.mark.asyncio
async def test_baggage_check_invalid_unit(client):
    """잘못된 단위 처리 테스트."""
    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
            "value": 15.6,
            "unit": "invalid_unit"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert "유효하지 않은 단위" in data.get("detail", "")


@pytest.mark.asyncio
async def test_baggage_check_missing_value_unit(client):
    """수량이나 단위가 없는 경우 테스트."""
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    # 수량이나 단위가 없으면 "조건부 가능" 반환
    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 조건부 가능인지 확인 (수량/단위가 없으면)
    assert data["carry_on"]["verdict"] == "conditional"
    assert "조건부" in data["carry_on"]["label"]
    assert data["checked"]["verdict"] == "conditional"


@pytest.mark.asyncio
async def test_baggage_check_unknown_item(client, test_session_with_data, monkeypatch):
    """알 수 없는 제품 처리 테스트."""
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "알 수 없는 제품",
            "value": 10.0,
            "unit": "cm"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 규칙이 없으면 "조건부 가능" 반환
    assert data["carry_on"]["verdict"] == "conditional"
    assert "알 수 없는 제품" in data["carry_on"]["reason"] or "규칙 정보가 없습니다" in data["carry_on"]["reason"]


@pytest.mark.asyncio
async def test_verdict_response_conversion(client, test_session_with_data, monkeypatch):
    """VerdictResponse 변환 테스트."""
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
            "value": 15.6,
            "unit": "inch"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # VerdictResponse 필드 검증
    carry_on = data["carry_on"]
    assert "verdict" in carry_on
    assert "label" in carry_on
    assert "reason" in carry_on
    assert "emoji" in carry_on
    assert "color_code" in carry_on
    assert "is_allowed" in carry_on
    assert "is_forbidden" in carry_on

    # 데이터 타입 검증
    assert isinstance(carry_on["verdict"], str)
    assert isinstance(carry_on["label"], str)
    assert isinstance(carry_on["emoji"], str)
    assert isinstance(carry_on["color_code"], str)
    assert isinstance(carry_on["is_allowed"], bool)
    assert isinstance(carry_on["is_forbidden"], bool)

    # checked도 동일하게 검증
    checked = data["checked"]
    assert "verdict" in checked
    assert "label" in checked
    assert "reason" in checked
    assert "emoji" in checked
    assert "color_code" in checked
    assert "is_allowed" in checked
    assert "is_farbidden" in checked


@pytest.mark.asyncio
async def test_baggage_check_size_exceeded(client, test_session_with_data, monkeypatch):
    """크기 초과 시 테스트."""
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    # 노트북 규칙: 기내용 16x9x9인치 (약 35.5cm)
    # 20x20x20인치 (약 50.8cm)는 초과
    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "노트북",
            "value": 20.0,
            "unit": "inch"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 크기 초과로 "불가" 판정
    assert data["carry_on"]["verdict"] == "forbidden"
    assert "불가" in data["carry_on"]["label"]
    assert "❌" in data["carry_on"]["emoji"]
    assert "초과" in data["carry_on"]["reason"] or "초과" in data["carry_on"]["label"]


@pytest.mark.asyncio
async def test_baggage_check_weight_exceeded(client, test_session_with_data, monkeypatch):
    """무게 초과 시 테스트."""
    async def get_baggage_service(session):
        repo = SQLAlchemyBaggageRuleRepository(session)
        return BaggageService(repo)

    app.dependency_overrides[BaggageService] = get_baggage_service

    # 보조배터리 규칙: 위탁 160Wh 초과 불가
    response = client.post(
        "/api/v1/baggage/check",
        json={
            "airline": "대한항공",
            "product": "보조배터리",
            "value": 200.0,
            "unit": "wh"
        },
        headers={"Authorization": "Bearer test_token"}
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    # 무게 초과로 "불가" 판정
    assert data["checked"]["verdict"] == "forbidden"
    assert "불가" in data["checked"]["label"]
    assert "초과" in data["checked"]["reason"]