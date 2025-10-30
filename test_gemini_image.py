#!/usr/bin/env python3
"""Quick test of Gemini image generation API"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import time

load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("❌ No GEMINI_API_KEY found")
    exit(1)

print(f"✅ API Key found: {GEMINI_API_KEY[:10]}...")

try:
    print("🔄 Initializing client...")
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✅ Client initialized")

    print("🎨 Testing image generation with gemini-2.5-flash-image-preview...")
    start = time.time()

    response = client.models.generate_content(
        model='gemini-2.5-flash-image-preview',
        contents=["A simple red square on white background"]
    )

    elapsed = time.time() - start
    print(f"✅ Generation completed in {elapsed:.2f}s")

    # Check if we got image data
    has_image = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            has_image = True
            print(f"✅ Image data received: {len(part.inline_data.data)} bytes")
            break

    if not has_image:
        print("❌ No image data in response")
        print(f"Response: {response}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

