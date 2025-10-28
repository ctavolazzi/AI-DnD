#!/usr/bin/env python3
"""
Example 1: Basic Character Generation
Demonstrates simple character creation with PixelLab
"""

import sys
sys.path.insert(0, '..')

from pixellab_client import PixelLabClient
import logging

logging.basicConfig(level=logging.INFO)


def main():
    # Initialize client with your API key
    API_KEY = "your-api-key-here"  # Replace with your actual key
    client = PixelLabClient(
        api_key=API_KEY,
        auto_save=True,
        save_dir="outputs/basic_characters"
    )

    print("=" * 60)
    print("PIXELLAB - BASIC CHARACTER GENERATION")
    print("=" * 60)

    # Check API balance
    balance = client.get_balance()
    print(f"\nAPI Credits: {balance['credits']}")

    # Example 1: Simple wizard
    print("\n1. Generating wizard character...")
    wizard = client.generate_character(
        description="fantasy wizard with blue robes and staff",
        width=64,
        height=64
    )
    print(f"   Generated: {wizard.size}")

    # Example 2: Knight with customization
    print("\n2. Generating knight with custom parameters...")
    knight = client.generate_character(
        description="medieval knight with sword and shield",
        width=64,
        height=64,
        outline='thick',  # Thick outline
        shading='smooth',  # Smooth shading
        detail='high',  # High detail
        view='side',  # Side view
        direction='east'  # Facing east
    )
    print(f"   Generated: {knight.size}")

    # Example 3: Isometric character
    print("\n3. Generating isometric character...")
    iso_char = client.generate_character(
        description="pixel art robot character",
        width=64,
        height=64,
        isometric=True,  # Isometric projection
        no_background=True  # Transparent background
    )
    print(f"   Generated: {iso_char.size}")

    # Example 4: Character with seed (reproducible)
    print("\n4. Generating reproducible character with seed...")
    seeded = client.generate_character(
        description="cute dragon companion",
        width=64,
        height=64,
        seed=42,  # Same seed = same result
        text_guidance_scale=10  # Higher = more literal interpretation
    )
    print(f"   Generated: {seeded.size}")

    # Example 5: Negative prompts
    print("\n5. Generating character with negative prompts...")
    specific = client.generate_character(
        description="warrior character",
        width=64,
        height=64,
        negative_description="no helmet, no armor"  # What to avoid
    )
    print(f"   Generated: {specific.size}")

    print("\n✓ All images saved to: outputs/basic_characters/")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
