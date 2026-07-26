"""baggage_rules 데이터 확인 스크립트."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://trapkit:trapkit_password@localhost:5432/trapkit")


async def verify_data():
    """baggage_rules 데이터 확인."""
    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        # 데이터 확인
        result = await conn.execute(text("""
            SELECT item_key, display_name, carry_on_rule, checked_rule
            FROM baggage_rules
            LIMIT 3;
        """))

        rows = result.fetchall()

        if not rows:
            print("[ERROR] No data in baggage_rules table")
            return

        print("[OK] baggage_rules data samples:")
        for row in rows:
            item_key, display_name, carry_on, checked = row
            print(f"  - {item_key}: {display_name}")
            print(f"    Carry-on: {carry_on}")
            print(f"    Checked: {checked}")
            print()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(verify_data())