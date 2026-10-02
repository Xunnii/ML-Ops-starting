import requests

LM_STUDIO_URL = "http://172.19.192.1:1234/v1/chat/completions"
MODEL = "qwen2.5-vl-7b-instruct"

prompt = """
Jawab dalam format JSON dengan kunci:
summary, priority, reason, missing_info.

Tiket:
Pembayaran gagal dan saldo terpotong.
"""

response = requests.post(
    LM_STUDIO_URL,
    json={
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0
    },
    timeout=120
)

response.raise_for_status()

result = response.json()

print(result["choices"][0]["message"]["content"])
