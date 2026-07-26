"""baggage_rules 테이블 복구 스크립트."""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://trapkit:trapkit_password@localhost:5432/trapkit")


async def restore_baggage_rules():
    """baggage_rules table restore."""
    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Check table existence
        result = await conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'baggage_rules'
            );
        """))
        exists = result.scalar()

        if exists:
            print("[OK] baggage_rules table already exists.")
            return

        print("[INFO] baggage_rules table does not exist. Creating...")

        # Create table
        await conn.execute(text("""
            CREATE TABLE baggage_rules (
                id SERIAL PRIMARY KEY,
                item_key VARCHAR(100) NOT NULL UNIQUE,
                display_name VARCHAR(200) NOT NULL,
                aliases JSON NOT NULL,
                unit VARCHAR(50) NOT NULL,
                carry_on_rule JSON NOT NULL,
                checked_rule JSON NOT NULL,
                tips TEXT,
                source VARCHAR(50) DEFAULT 'iata' NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
            );
        """))

        # Create index
        await conn.execute(text("""
            CREATE INDEX idx_baggage_rules_item_key ON baggage_rules(item_key);
        """))

        print("[OK] baggage_rules table created successfully")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(restore_baggage_rules())