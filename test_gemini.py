"""Standalone connectivity check for the configured Gemini model.

Run with:  .venv-linux/bin/python test_gemini.py
"""

import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

try:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=model,
        contents="Confirm connection for HackMatch AI.",
    )
    print(f"✅ Success! {model} responded:")
    print(response.text)
except Exception as e:  # noqa: BLE001
    print(f"❌ Connection Error ({model}):", e)
