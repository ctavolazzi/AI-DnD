#!/usr/bin/env python3
"""
Simple test script to generate ONE image with Nano Banana
and save it as a PNG file that we can open in the browser.
"""

import os
import sys
from io import BytesIO
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    sys.exit(1)

print("🍌 Nano Banana Image Generation Test")
print("=" * 60)

# Initialize client
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("✓ Gemini client initialized")
except Exception as e:
    print(f"❌ Failed to initialize client: {e}")
    sys.exit(1)

# Define the prompt
prompt = """
A photorealistic scene of the entrance to Emberpeak, a mountain village at dawn.
Stone archway covered in moss, cobblestone path leading into the village,
misty mountain peaks in the background, warm torchlight from the gate,
fantasy RPG setting, cinematic lighting, detailed environment.
"""

print("\n📝 Prompt:")
print(prompt.strip())
print("\n🎨 Generating image...")
print("   (This may take 5-10 seconds)")

try:
    # Generate the image
    response = client.models.generate_content(
        model='gemini-2.5-flash-image',
        contents=[prompt],
        config=types.GenerateContentConfig(
            response_modalities=['Image'],
            image_config=types.ImageConfig(
                aspect_ratio='16:9',
            )
        )
    )

    # Extract and save the image
    image_saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            # Open image from bytes
            image = Image.open(BytesIO(part.inline_data.data))

            # Save as PNG
            output_path = 'emberpeak_entrance.png'
            image.save(output_path, format='PNG')

            print(f"\n✅ Image generated successfully!")
            print(f"📁 Saved to: {os.path.abspath(output_path)}")
            print(f"📐 Size: {image.size[0]}x{image.size[1]} pixels")
            print(f"💾 Format: PNG")

            image_saved = True
            break

    if not image_saved:
        print("❌ No image data found in response")
        sys.exit(1)

    # Open the image in default browser/viewer
    print("\n🌐 Opening image in browser...")
    os.system(f'open {output_path}')

    print("\n" + "=" * 60)
    print("✨ Success! Check your browser for the generated image.")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Error generating image:")
    print(f"   {str(e)}")

    # Check if it's a quota error
    if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
        print("\n💡 Quota exceeded. Options:")
        print("   1. Wait for quota to reset (usually daily)")
        print("   2. Check usage: https://ai.dev/usage?tab=rate-limit")
        print("   3. Try a different API key")
        print("   4. Upgrade to paid tier")

    sys.exit(1)


