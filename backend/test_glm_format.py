import asyncio
import json

from app.config import settings
from app.application.commands.create_trip import CreateTripCommand
from infrastructure.external.glm_client import GLMClient

async def test():
    print("=== GLM Response Format Test ===")
    print()

    command = CreateTripCommand(
        user_id="test-user",
        destination="제주도",
        purpose=["관광"],
        duration_nights=3,
        departure_month=8,
        companions="가족",
    )

    client = GLMClient()

    try:
        content = await client.generate_trip_content(command)
        print("Response keys:", list(content.keys()))
        print()

        if "cautions" in content:
            print(f"Cautions: {len(content['cautions'])} items")
            for item in content["cautions"][:2]:
                print(f"  {item}")

        if "baggage_summary" in content:
            print(f"Baggage summary: {len(content['baggage_summary'])} items")
            for item in content["baggage_summary"][:2]:
                print(f"  {item}")
        elif "items" in content:
            print(f"Items (unexpected): {len(content['items'])} items")
            for item in content["items"][:2]:
                print(f"  {item}")

        if "baggage_summary" not in content and "items" not in content:
            print("WARNING: No baggage summary found!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())