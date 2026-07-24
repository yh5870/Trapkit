"""Supabase baggage_rules 데이터 삽입 스크립트."""

import asyncio
import os
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres.ihokiffmjcvtstyinpiw:Tjswns0437!!@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres")


BAGGAGE_RULES = [
    # 전자기기
    {
        "item_key": "koreanair:macbook",
        "display_name": "맥북",
        "aliases": ["macbook pro", "mac pro", "laptop", "notebook"],
        "unit": "inch",
        "carry_on_rule": {"max_size_cm": 40, "max_weight_kg": 7, "restrictions": [{"category": "electronic", "value": "lithium_100wh"}]},
        "checked_rule": {"max_size_cm": 158, "max_weight_kg": 23, "restrictions": [{"category": "electronic", "value": "lithium_160wh"}]},
        "tips": "배터리 100Wh 이하는 기내 반입 가능"
    },
    {
        "item_key": "koreanair:iphone",
        "display_name": "아이폰",
        "aliases": ["smartphone", "phone", "mobile"],
        "unit": "count",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "electronic", "value": "lithium_allowed"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "electronic", "value": "forbidden"}]},
        "tips": "기내 반입 필수, 위탁 금지"
    },
    {
        "item_key": "asiana:laptop",
        "display_name": "노트북",
        "aliases": ["macbook", "thinkpad", "dell"],
        "unit": "inch",
        "carry_on_rule": {"max_size_cm": 40, "max_weight_kg": 10, "restrictions": []},
        "checked_rule": {"max_size_cm": 158, "max_weight_kg": 32, "restrictions": [{"category": "electronic", "value": "lithium_100wh"}]},
        "tips": "배터리는 반드시 기내 반입"
    },
    {
        "item_key": "japanairlines:tablet",
        "display_name": "태블릿",
        "aliases": ["ipad", "galaxy tab"],
        "unit": "inch",
        "carry_on_rule": {"max_size_cm": 40, "max_weight_kg": 10, "restrictions": []},
        "checked_rule": {"max_size_cm": 100, "max_weight_kg": 10, "restrictions": [{"category": "electronic", "value": "lithium_160wh"}]},
        "tips": "전원 OFF 또는 비행 모드"
    },
    # 액체
    {
        "item_key": "koreanair:cosmetics",
        "display_name": "화장품",
        "aliases": ["skincare", "toiletries"],
        "unit": "ml",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 1, "restrictions": [{"category": "liquid", "value": "max_100ml_each"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": []},
        "tips": "기내 반입 시 1리터 투명 비닐봉지에 담아야 함"
    },
    {
        "item_key": "asiana:beverage",
        "display_name": "음료수",
        "aliases": ["water", "juice", "drink"],
        "unit": "ml",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 0.1, "restrictions": [{"category": "liquid", "value": "max_100ml"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": []},
        "tips": "면세점 구매 음료는 기내 반입 가능"
    },
    # 의료품
    {
        "item_key": "koreanair:medicine",
        "display_name": "의약품",
        "aliases": ["prescription", "medical"],
        "unit": "ml",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 1, "restrictions": [{"category": "medical", "value": "prescription_required"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": []},
        "tips": "처방전 또는 의료진 확인서 지참"
    },
    {
        "item_key": "asiana:inhaler",
        "display_name": "인헤일러",
        "aliases": ["asthma", "respiratory"],
        "unit": "count",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "medical", "value": "allowed"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "medical", "value": "forbidden"}]},
        "tips": "기내 반입 필수"
    },
    {
        "item_key": "japanairlines:insulin",
        "display_name": "인슐린",
        "aliases": ["diabetes", "diabetic"],
        "unit": "ml",
        "carry_on_rule": {"max_size_cm": 0, "max_weight_kg": 1, "restrictions": [{"category": "medical", "value": "ice_pack_allowed"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "medical", "value": "forbidden"}]},
        "tips": "아이스팩 사용 가능"
    },
    {
        "item_key": "delta:medical_equipment",
        "display_name": "의료 장비",
        "aliases": ["cpap", "oxygen"],
        "unit": "count",
        "carry_on_rule": {"max_size_cm": 50, "max_weight_kg": 10, "restrictions": [{"category": "medical", "value": "notification_required"}]},
        "checked_rule": {"max_size_cm": 0, "max_weight_kg": 0, "restrictions": [{"category": "medical", "value": "forbidden"}]},
        "tips": "항공사 미리 통지 필요"
    },
]


async def insert_data():
    """Insert baggage rules data."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # Clear existing data
        await conn.execute(text("DELETE FROM baggage_rules"))
        print("[OK] Cleared existing data")

        # Insert new data
        for rule in BAGGAGE_RULES:
            await conn.execute(
                text("""
                    INSERT INTO baggage_rules (item_key, display_name, aliases, unit, carry_on_rule, checked_rule, tips, source)
                    VALUES (:item_key, :display_name, :aliases, :unit, :carry_on_rule, :checked_rule, :tips, :source)
                    ON CONFLICT (item_key) DO NOTHING
                """),
                {
                    "item_key": rule["item_key"],
                    "display_name": rule["display_name"],
                    "aliases": json.dumps(rule["aliases"]),
                    "unit": rule["unit"],
                    "carry_on_rule": json.dumps(rule["carry_on_rule"]),
                    "checked_rule": json.dumps(rule["checked_rule"]),
                    "tips": rule.get("tips", ""),
                    "source": rule.get("source", "iata"),
                }
            )
            print(f"[OK] Inserted: {rule['item_key']}")

        print(f"[OK] Total {len(BAGGAGE_RULES)} rules inserted successfully")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(insert_data())