#!/usr/bin/env python3
"""
Fixed PixelLab API Test - Correct Image Handling
Test the actual API methods with proper image handling
"""

import pixellab
import os
from pixellab.models import ImageSize
import base64
from io import BytesIO
from PIL import Image

def test_character_generation():
    """Test character generation with correct image handling."""
    print("🎨 PixelLab Character Generation Test")
    print("=" * 50)

    # Initialize client
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("Please set your API key: export PIXELLAB_API_KEY=your_key_here")
        return
    client = pixellab.Client(secret=API_KEY)

    try:
        # Test balance endpoint
        print("1. Testing balance endpoint...")
        balance_response = client.get_balance()
        print(f"   Balance: ${balance_response.usd} USD")

        # Test character generation with PixFlux
        print("\n2. Testing character generation (PixFlux)...")
        character_response = client.generate_image_pixflux(
            description="fantasy wizard with blue robes and staff",
            image_size=ImageSize(width=64, height=64)
        )
        print(f"   Character generated successfully!")
        print(f"   Response type: {type(character_response)}")

        # Handle the image properly
        if hasattr(character_response, 'image') and character_response.image:
            print(f"   Image type: {type(character_response.image)}")

            # Try different ways to access the image data
            if hasattr(character_response.image, 'base64'):
                image_data = base64.b64decode(character_response.image.base64)
            elif hasattr(character_response.image, '__str__'):
                image_data = base64.b64decode(str(character_response.image))
            else:
                # Try to convert to string first
                image_str = str(character_response.image)
                if image_str.startswith('data:image'):
                    # Remove data URL prefix
                    image_str = image_str.split(',')[1]
                image_data = base64.b64decode(image_str)

            # Save to file
            with open("test_wizard.png", "wb") as f:
                f.write(image_data)
            print(f"   Image saved as: test_wizard.png")

            # Get image info
            img = Image.open(BytesIO(image_data))
            print(f"   Image size: {img.size}")
            print(f"   Image mode: {img.mode}")

        # Test BitForge generation
        print("\n3. Testing style transfer (BitForge)...")
        try:
            bitforge_response = client.generate_image_bitforge(
                description="medieval knight with sword and shield",
                image_size=ImageSize(width=64, height=64)
            )
            print(f"   BitForge generation successful!")

            if hasattr(bitforge_response, 'image') and bitforge_response.image:
                if hasattr(bitforge_response.image, 'base64'):
                    image_data = base64.b64decode(bitforge_response.image.base64)
                else:
                    image_data = base64.b64decode(str(bitforge_response.image))

                with open("test_knight.png", "wb") as f:
                    f.write(image_data)
                print(f"   Image saved as: test_knight.png")

        except Exception as e:
            print(f"   BitForge error: {e}")

        print("\n✅ All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_character_generation()
