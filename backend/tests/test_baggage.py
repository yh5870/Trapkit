"""수화물 체커 API 테스트."""

from fastapi import status


async def test_check_baggage_power_bank(client):
    """보조배터리 판정 테스트."""
    response = await client.post(
        "/api/baggage/check",
        json={
            "item": "보조배터리",
            "value": 20000,
            "unit": "mAh",
            "flight_type": "international",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["item"] == "보조배터리"
    assert data["normalized_key"] == "power_bank"
    assert "converted" in data
    assert data["carry_on"]["verdict"] == "allowed"
    assert data["checked"]["verdict"] == "forbidden"
    assert data["source"] == "rule_db"


async def test_check_baggage_sunscreen(client):
    """선크림 판정 테스트."""
    response = await client.post(
        "/api/baggage/check",
        json={
            "item": "선크림",
            "value": 150,
            "unit": "ml",
            "flight_type": "international",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["item"] == "선크림"
    assert data["normalized_key"] == "sunscreen"
    assert data["carry_on"]["verdict"] == "forbidden"
    assert data["checked"]["verdict"] == "allowed"


async def test_check_baggage_unknown(client):
    """알 수 없는 품목 판정 테스트 (AI 폴백)."""
    response = await client.post(
        "/api/baggage/check",
        json={
            "item": "알 수 없는 품목",
            "flight_type": "international",
        },
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["source"] == "ai"
    assert data["carry_on"]["verdict"] == "conditional"