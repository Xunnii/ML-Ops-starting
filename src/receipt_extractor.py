import base64
import json
import os
from pathlib import Path

import requests


# =========================
# CONFIGURATION
# =========================

IMAGE = Path("data/raw/nota-sample.png")

MODEL = os.environ["LM_STUDIO_MODEL"]

LM_STUDIO_URL = "http://172.19.192.1:1234/v1/chat/completions"


# =========================
# CHECK IMAGE
# =========================

if not IMAGE.exists():
    raise FileNotFoundError(
        f"File gambar tidak ditemukan: {IMAGE}"
    )

if IMAGE.stat().st_size == 0:
    raise ValueError(
        f"File gambar kosong: {IMAGE}"
    )


# =========================
# ENCODE IMAGE
# =========================

image_base64 = base64.b64encode(
    IMAGE.read_bytes()
).decode("utf-8")


# =========================
# PROMPT
# =========================

prompt = """
Baca nota pada gambar.

Ekstrak informasi berikut:
- merchant
- tanggal
- item
- subtotal
- pajak
- total

Keluarkan HANYA JSON valid dengan struktur:

{
  "merchant": "...",
  "date": "...",
  "items": [
    {
      "name": "...",
      "quantity": 1,
      "price": 0
    }
  ],
  "subtotal": 0,
  "tax": 0,
  "total": 0
}

Aturan:
- Jika pajak tidak terlihat, isi 0.
- Jangan mengarang informasi.
- Gunakan angka tanpa simbol mata uang.
- Ekstrak semua item yang terlihat pada nota.
"""


# =========================
# CALL LM STUDIO
# =========================

response = requests.post(
    LM_STUDIO_URL,
    json={
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0
    },
    timeout=120
)


# =========================
# CHECK RESPONSE
# =========================

print("STATUS:", response.status_code)

if response.status_code != 200:
    print("RESPONSE:", response.text)

response.raise_for_status()


# =========================
# GET MODEL OUTPUT
# =========================

data = response.json()

prediction = data["choices"][0]["message"]["content"]

print("\nRAW OUTPUT:")
print(prediction)


# =========================
# CLEAN JSON
# =========================

prediction = prediction.strip()

if prediction.startswith("```json"):
    prediction = prediction[7:]

elif prediction.startswith("```"):
    prediction = prediction[3:]

if prediction.endswith("```"):
    prediction = prediction[:-3]

prediction = prediction.strip()


# =========================
# PARSE JSON
# =========================

result = json.loads(prediction)


# =========================
# SAVE RESULT
# =========================

Path("reports").mkdir(exist_ok=True)

Path("reports/receipt.json").write_text(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


# =========================
# PRINT RESULT
# =========================

print("\nHASIL EKSTRAKSI:")
print(
    json.dumps(
        result,
        indent=2,
        ensure_ascii=False
    )
)

print("\nTersimpan di: reports/receipt.json")