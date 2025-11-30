#!/usr/bin/env python3
"""Test Nano Banana image generation directly."""

import requests
import json

BASE_URL = "http://localhost:5000"

print("🎨 Testing Nano Banana Image Generation")
print("="*60 + "\n")

# Test 1: Health check
print("1️⃣ Checking server health...")
try:
    response = requests.get(f"{BASE_URL}/health")
    if response.status_code == 200:
        print("✅ Server is healthy!\n")
    else:
        print(f"⚠️  Server response: {response.status_code}\n")
except Exception as e:
    print(f"❌ Could not reach server: {e}\n")
    exit(1)

# Test 2: Generate a D&D scene
print("2️⃣ Generating epic D&D scene...")
print("   Scene: A dwarven warrior at the gates of an ancient mountain fortress\n")

scene_data = {
    "description": "A mighty dwarven warrior named Thorin Ironfist stands before the massive ancient gates of Ironforge Mountain. The gates are ornately carved with runes and dwarf kings. Thunder clouds gather overhead as the sun sets, casting dramatic orange light across the stone. Epic fantasy art, detailed, atmospheric.",
    "aspect_ratio": "16:9"
}

try:
    response = requests.post(
        f"{BASE_URL}/generate-scene",
        json=scene_data,
        timeout=60
    )

    if response.status_code == 200:
        result = response.json()
        print("✅ Scene generated successfully!\n")

        if 'image_url' in result:
            print(f"🖼️  Image URL: {result['image_url']}")

        if 'image_data' in result:
            # Save the image
            import base64
            image_data = result['image_data']
            if image_data.startswith('data:image'):
                # Extract base64 data
                base64_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(base64_data)

                filename = "generated_dwarven_fortress.png"
                with open(filename, 'wb') as f:
                    f.write(image_bytes)
                print(f"💾 Image saved to: {filename}")
                print(f"   Open it with: open {filename}")

        # Save full response
        with open('image_generation_result.json', 'w') as f:
            # Remove large base64 data for readability
            save_result = result.copy()
            if 'image_data' in save_result:
                save_result['image_data'] = '[base64 data removed for readability]'
            json.dump(save_result, f, indent=2)
        print(f"📄 Response metadata saved to: image_generation_result.json\n")

    else:
        print(f"❌ Generation failed: HTTP {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("⏱️  Request timed out - image generation can take 30-60 seconds")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎨 Image generation test complete!")
print("="*60)
