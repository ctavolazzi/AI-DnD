#!/usr/bin/env python3
"""
PixelLab Animation Test - Complete Working Version
Test character animation generation and save all frames
"""

import pixellab
import os
from pixellab.models import ImageSize
import base64
from io import BytesIO
from PIL import Image

def test_animation_complete():
    """Test character animation generation and save frames."""
    print("🎬 PixelLab Animation Test - Complete")
    print("=" * 50)

    # Initialize client
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("Please set your API key: export PIXELLAB_API_KEY=your_key_here")
        return
    client = pixellab.Client(secret=API_KEY)

    try:
        # First generate a base character
        print("1. Generating base character...")
        base_character = client.generate_image_pixflux(
            description="fantasy warrior with sword",
            image_size=ImageSize(width=64, height=64)
        )

        if hasattr(base_character, 'image') and base_character.image:
            # Convert Base64Image to PIL Image
            image_data = base64.b64decode(base_character.image.base64)
            pil_image = Image.open(BytesIO(image_data))

            # Save base character
            pil_image.save("warrior_base.png")
            print("   Base character saved as: warrior_base.png")

        # Test text-based animation
        print("\n2. Testing text-based animation...")
        animation_response = client.animate_with_text(
            description="fantasy warrior with sword",
            negative_description="blurry, low quality, distorted",
            action="walk",
            reference_image=pil_image,
            image_size=ImageSize(width=64, height=64),
            n_frames=4
        )

        print("   Animation generated successfully!")

        # Save animation frames
        if hasattr(animation_response, 'images') and animation_response.images:
            print(f"   Number of frames: {len(animation_response.images)}")

            # Save each frame
            for i, frame_image in enumerate(animation_response.images):
                if hasattr(frame_image, 'base64'):
                    frame_data = base64.b64decode(frame_image.base64)
                    frame_pil = Image.open(BytesIO(frame_data))
                    filename = f"warrior_walk_frame_{i+1}.png"
                    frame_pil.save(filename)
                    print(f"   Frame {i+1} saved as: {filename}")

        # Test different actions
        print("\n3. Testing attack animation...")
        attack_response = client.animate_with_text(
            description="fantasy warrior with sword",
            negative_description="blurry, low quality, distorted",
            action="attack",
            reference_image=pil_image,
            image_size=ImageSize(width=64, height=64),
            n_frames=4
        )

        if hasattr(attack_response, 'images') and attack_response.images:
            print(f"   Attack frames: {len(attack_response.images)}")
            for i, frame_image in enumerate(attack_response.images):
                if hasattr(frame_image, 'base64'):
                    frame_data = base64.b64decode(frame_image.base64)
                    frame_pil = Image.open(BytesIO(frame_data))
                    filename = f"warrior_attack_frame_{i+1}.png"
                    frame_pil.save(filename)
                    print(f"   Attack frame {i+1} saved as: {filename}")

        print("\n✅ Animation tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_animation_complete()
