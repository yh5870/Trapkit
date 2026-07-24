import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_data():
    database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(database_url)

    # 총 규칙 수 확인
    count = await conn.fetchval('SELECT COUNT(*) FROM baggage_rules')
    print(f'Total rules: {count}')

    # 규칙 10개 샘플 조회
    rows = await conn.fetch('SELECT item_key, display_name FROM baggage_rules LIMIT 10')
    for row in rows:
        print(f'  - {row["item_key"]}: {row["display_name"]}')

    await conn.close()

asyncio.run(check_data())