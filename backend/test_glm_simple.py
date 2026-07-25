"""Simple GLM API Test."""

from zai import ZhipuAiClient
from app.config import settings

print("=" * 60)
print("Simple GLM API Test")
print("=" * 60)
print()

# Initialize client
print("Initializing ZhipuAiClient...")
print(f"API Key: {settings.GLM_API_KEY[:30]}...")
print()

try:
    client = ZhipuAiClient(api_key=settings.GLM_API_KEY)
    print("Client initialized successfully!")
    print()

    # Simple test
    print("Calling API...")
    response = client.chat.completions.create(
        model="glm-4",
        messages=[
            {"role": "user", "content": "Hello, please say hi in JSON format"}
        ],
        max_tokens=100,
    )

    print("Response:")
    print(response.choices[0].message.content)
    print()

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()