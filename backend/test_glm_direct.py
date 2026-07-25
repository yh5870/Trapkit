import httpx
import json

r = httpx.post(
    'https://open.bigmodel.cn/api/paas/v4/chat/completions',
    json={'model': 'glm-4', 'messages': [{'role': 'user', 'content': 'hi'}]},
    headers={'Authorization': 'Bearer 45d7c7980c304f5489c9184339e235c6.YxJ4BdM4ZwJjfCHG', 'Content-Type': 'application/json'}
)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")