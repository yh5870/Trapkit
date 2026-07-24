import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def validate_data():
    database_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg://', 'postgresql://')
    conn = await asyncpg.connect(database_url)

    print("=== Baggage Rules Data Validation ===")
    print()

    # 1. 총 규칙 수 확인
    count = await conn.fetchval('SELECT COUNT(*) FROM baggage_rules')
    print(f"1. Total rules: {count} / Expected: 25")
    print(f"   Status: {'PASS' if count == 25 else 'FAIL'}")
    print()

    # 2. 카테고리별 개수 확인
    categories = await conn.fetch("""
        SELECT
            CASE
                WHEN item_key IN ('laptop', 'tablet', 'power_bank', 'smartphone') THEN 'Electronics'
                WHEN item_key IN ('liquid_container_100ml', 'alcohol') THEN 'Liquids'
                WHEN item_key IN ('medicine_liquid', 'insulin', 'medical_device', 'baby_formula_liquid') THEN 'Medical'
                WHEN item_key LIKE 'sports_%' THEN 'Sports'
                WHEN item_key LIKE 'food_%' THEN 'Food'
                ELSE 'Others'
            END as category,
            COUNT(*) as count
        FROM baggage_rules
        GROUP BY category
        ORDER BY category
    """)

    print("2. Category breakdown:")
    for cat in categories:
        print(f"   - {cat['category']}: {cat['count']}")
    print()

    # 3. item_key 중복 확인
    duplicates = await conn.fetch("""
        SELECT item_key, COUNT(*) as count
        FROM baggage_rules
        GROUP BY item_key
        HAVING COUNT(*) > 1
    """)
    print(f"3. Duplicate item_keys: {len(duplicates)}")
    print(f"   Status: {'PASS' if len(duplicates) == 0 else 'FAIL'}")
    print()

    # 4. JSON 필드 유효성 확인
    null_json = await conn.fetch("""
        SELECT item_key
        FROM baggage_rules
        WHERE carry_on_rule IS NULL OR checked_rule IS NULL OR aliases IS NULL
    """)
    print(f"4. NULL JSON fields: {len(null_json)}")
    print(f"   Status: {'PASS' if len(null_json) == 0 else 'FAIL'}")
    if len(null_json) > 0:
        for row in null_json:
            print(f"   - {row['item_key']}")
    print()

    # 5. source 필드 확인
    wrong_source = await conn.fetch("""
        SELECT item_key, source
        FROM baggage_rules
        WHERE source != 'iata'
    """)
    print(f"5. Non-IATA sources: {len(wrong_source)}")
    print(f"   Status: {'PASS' if len(wrong_source) == 0 else 'FAIL'}")
    if len(wrong_source) > 0:
        for row in wrong_source:
            print(f"   - {row['item_key']}: {row['source']}")
    print()

    # 6. 샘플 데이터 확인 (laptop)
    laptop = await conn.fetchrow("SELECT * FROM baggage_rules WHERE item_key = 'laptop'")
    if laptop:
        print("6. Sample data (laptop):")
        print(f"   - item_key: {laptop['item_key']}")
        print(f"   - display_name: {laptop['display_name']}")
        print(f"   - unit: {laptop['unit']}")
        print(f"   - source: {laptop['source']}")
        print(f"   - Status: PASS")
    else:
        print("6. Sample data (laptop): NOT FOUND - FAIL")
    print()

    # 7. 전체 결과
    all_pass = (
        count == 25 and
        len(duplicates) == 0 and
        len(null_json) == 0 and
        len(wrong_source) == 0 and
        laptop is not None
    )

    print("=== Summary ===")
    print(f"Overall Status: {'PASS' if all_pass else 'FAIL'}")
    if all_pass:
        print("All validations passed successfully!")
    else:
        print("Some validations failed. Please check the results above.")

    await conn.close()

asyncio.run(validate_data())