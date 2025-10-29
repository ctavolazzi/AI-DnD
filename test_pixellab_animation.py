#!/usr/bin/env python3
"""
PixelLab Animation Test
Test character animation generation
"""

import pixellab
import os
from pixellab.models import ImageSize
import base64
from io import BytesIO
from PIL import Image

def test_animation():
    """Test character animation generation."""
    print("🎬 PixelLab Animation Test")
    print("=" * 40)

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
            # Save base character
            image_data = base64.b64decode(base_character.image.base64)
            with open("base_warrior.png", "wb") as f:
                f.write(image_data)
            print("   Base character saved as: base_warrior.png")

        # Test text-based animation
        print("\n2. Testing text-based animation...")
        try:
            animation_response = client.animate_with_text(
                description="fantasy warrior with sword",
                action="walk",
                reference_image=base_character.image,
                image_size=ImageSize(width=64, height=64),
                n_frames=4
            )
            print("   Animation generated successfully!")

            if hasattr(animation_response, 'frames') and animation_response.frames:
                print(f"   Number of frames: {len(animation_response.frames)}")

                # Save each frame
                for i, frame in enumerate(animation_response.frames):
                    if hasattr(frame, 'image') and frame.image:
                        frame_data = base64.b64decode(frame.image.base64)
                        filename = f"warrior_walk_frame_{i+1}.png"
                        with open(filename, "wb") as f:
                            f.write(frame_data)
                        print(f"   Frame {i+1} saved as: {filename}")

        except Exception as e:
            print(f"   Animation error: {e}")
            import traceback
            traceback.print_exc()

        print("\n✅ Animation test completed!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_animation()
