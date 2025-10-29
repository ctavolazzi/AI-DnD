#!/usr/bin/env python3
"""
Example 5: Advanced Features
Demonstrates inpainting, skeleton animation, and style transfer
"""

import sys
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient
from PIL import Image, ImageDraw
import logging

logging.basicConfig(level=logging.INFO)


def create_simple_mask(width, height, mask_region):
    """Create a simple mask for inpainting demo."""
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rectangle(mask_region, fill=255)
    return mask


def main():
    API_KEY = "your-api-key-here"
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/advanced"
    )

    print("=" * 60)
    print("PIXELLAB - ADVANCED FEATURES")
    print("=" * 60)

    # Example 1: Style Transfer with BitForge
    print("\n1. Creating character with style transfer...")

    # Generate a style reference
    style_ref = client.generate_character(
        description="retro 8-bit game character",
        width=64,
        height=64
    )

    # Generate new character with that style
    styled_char = client.generate_with_style(
        description="fantasy elf archer",
        style_image=style_ref,
        width=64,
        height=64,
        style_strength=0.8
    )
    print("   Styled character created")

    # Example 2: Inpainting - Modify part of an image
    print("\n2. Demonstrating inpainting...")

    # Create base character
    original = client.generate_character(
        description="pixel art warrior",
        width=64,
        height=64,
        no_background=True
    )

    # Create a mask for the region to modify (e.g., change weapon)
    # In practice, you'd create this in an image editor
    # For demo, let's create a simple rectangular mask
    mask = create_simple_mask(64, 64, (40, 20, 60, 40))

    # Inpaint the masked region
    modified = client.inpaint_image(
        description="golden magic staff",
        inpainting_image=original,
        mask_image=mask,
        width=64,
        height=64
    )
    print("   Inpainted character created")

    # Example 3: Skeleton Extraction
    print("\n3. Extracting character skeleton...")

    test_char = client.generate_character(
        description="pixel art humanoid character standing",
        width=64,
        height=64,
        no_background=True
    )

    skeleton_data = client.estimate_skeleton(test_char)
    print(f"   Skeleton extracted with {len(skeleton_data['skeleton_frame'].keypoints) if skeleton_data.get('skeleton_frame') else 0} keypoints")

    # Example 4: Create variations
    print("\n4. Creating character variations...")

    base_description = "pixel art medieval soldier"

    # Generate multiple variations with different seeds
    variations = []
    for i in range(4):
        variation = client.generate_character(
            description=base_description,
            width=64,
            height=64,
            seed=i * 100  # Different seeds for variety
        )
        variations.append(variation)

    variation_sheet = client.create_sprite_sheet(
        variations,
        columns=4,
        filename="soldier_variations.png"
    )
    print(f"   Created {len(variations)} variations")

    # Example 5: High detail generation
    print("\n5. Generating high-detail character...")

    detailed = client.generate_character(
        description="ornate fantasy wizard with intricate robes and glowing staff",
        width=128,
        height=128,
        detail='high',
        text_guidance_scale=12,  # Very literal interpretation
        no_background=True
    )
    print("   High-detail character created")

    print("\n✓ All advanced features demonstrated!")
    print("✓ Outputs saved to: outputs/advanced/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
