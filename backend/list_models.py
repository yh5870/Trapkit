"""사용 가능한 Gemini 모델 목록 확인."""

from google import genai
from app.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

print("=== Available Gemini Models ===")
print()

for model in client.models.list():
    name = model.name
    # 디스플레이 이름에서 모델 이름 추출
    if "models/" in name:
        model_name = name.replace("models/", "")
        # generateContent 지원 여부 확인
        if hasattr(model, "supported_actions"):
            supports_generate = "generateContent" in model.supported_actions
            print(f"[{model_name}] - generateContent: {supports_generate}")
        else:
            print(f"[{model_name}]")