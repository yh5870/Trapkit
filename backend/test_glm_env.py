import os
os.environ["ZAI_API_KEY"] = "45d7c7980c304f5489c9184339e235c6.YxJ4BdM4ZwJjfCHG"

from zai import ZhipuAiClient

client = ZhipuAiClient()
print("OK")
response = client.chat.completions.create(
    model="glm-4",
    messages=[
        {"role": "user", "content": "Say hi"}
    ],
    max_tokens=10,
)
print(response.choices[0].message.content)