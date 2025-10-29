#!/usr/bin/env python3
"""
PixelLab Animation Debug
Debug the animation response structure
"""

import pixellab
import os
from pixellab.models import ImageSize
import base64
from io import BytesIO
from PIL import Image

def debug_animation():
    """Debug animation response structure."""
    print("🔍 PixelLab Animation Debug")
    print("=" * 40)

    # Initialize client
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("Please set your API key: export PIXELLAB_API_KEY=your_key_here")
        return
    client = pixellab.Client(secret=API_KEY)

    try:
        # Generate a base character
        print("1. Generating base character...")
        base_character = client.generate_image_pixflux(
            description="fantasy warrior with sword",
            image_size=ImageSize(width=64, height=64)
        )

        if hasattr(base_character, 'image') and base_character.image:
            image_data = base64.b64decode(base_character.image.base64)
            pil_image = Image.open(BytesIO(image_data))
            pil_image.save("debug_base_warrior.png")
            print("   Base character saved")

        # Test animation
        print("\n2. Testing animation...")
        animation_response = client.animate_with_text(
            description="fantasy warrior with sword",
            negative_description="blurry, low quality, distorted",
            action="walk",
            reference_image=pil_image,
            image_size=ImageSize(width=64, height=64),
            n_frames=4
        )

        print(f"   Animation response type: {type(animation_response)}")
        print(f"   Animation response attributes: {[attr for attr in dir(animation_response) if not attr.startswith('_')]}")

        # Check for frames
        if hasattr(animation_response, 'frames'):
            print(f"   Frames attribute: {animation_response.frames}")
            if animation_response.frames:
                print(f"   Number of frames: {len(animation_response.frames)}")
                for i, frame in enumerate(animation_response.frames):
                    print(f"   Frame {i}: {type(frame)}")
                    if hasattr(frame, 'image'):
                        print(f"     Frame image: {type(frame.image)}")
                    else:
                        print(f"     Frame attributes: {[attr for attr in dir(frame) if not attr.startswith('_')]}")

        # Check for other possible attributes
        for attr in ['images', 'animation', 'result', 'data']:
            if hasattr(animation_response, attr):
                value = getattr(animation_response, attr)
                print(f"   {attr}: {type(value)} = {value}")

        print("\n✅ Debug completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_animation()
