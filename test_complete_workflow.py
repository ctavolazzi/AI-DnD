#!/usr/bin/env python3
"""
Complete PixelLab + Nano Banana Workflow Test
Demonstrates organized file structure and AI-powered image cleanup
"""

import os
import sys
from pathlib import Path
from enhanced_pixellab_client import EnhancedPixelLabClient
from nano_banana_pixel_art_cleaner import NanoBananaPixelArtCleaner

def test_complete_workflow():
    """Test the complete PixelLab + Nano Banana workflow."""
    print("🎨 Complete PixelLab + Nano Banana Workflow Test")
    print("=" * 60)

    # Check for API keys
    pixellab_key = "b4567140-3203-42ec-be0e-3b995f61dc93"
    nano_banana_key = os.getenv("GEMINI_API_KEY")

    if not nano_banana_key:
        print("⚠️  GEMINI_API_KEY not found - will test without Nano Banana cleanup")
        print("   Set it with: export GEMINI_API_KEY='your-key'")
        nano_banana_key = None

    # Initialize enhanced client
    print("\n1. Initializing Enhanced PixelLab Client...")
    client = EnhancedPixelLabClient(
        api_key=pixellab_key,
        nano_banana_api_key=nano_banana_key
    )

    # Check balance
    balance = client.get_balance()
    print(f"   PixelLab balance: ${balance['credits']} USD")

    # Test character generation with cleanup
    print("\n2. Generating characters with cleanup...")

    characters = [
        ("fantasy wizard with blue robes and staff", "pixflux"),
        ("medieval knight with golden armor and sword", "bitforge"),
        ("dark elf rogue with daggers", "pixflux"),
        ("dwarf warrior with axe and shield", "bitforge")
    ]

    generated_characters = []
    for description, style in characters:
        print(f"\n   Generating: {description} ({style})")
        character = client.generate_character(
            description=description,
            style=style,
            clean_up=nano_banana_key is not None
        )
        generated_characters.append(character)

    # Test animation generation
    print("\n3. Generating animations...")

    # Use the first character for animation
    base_character = generated_characters[0]

    animations = [
        ("walk", "walking forward"),
        ("attack", "attacking with staff"),
        ("idle", "standing idle"),
        ("cast", "casting a spell")
    ]

    for action, description in animations:
        print(f"\n   Generating {action} animation...")
        frames = client.generate_animation(
            description="fantasy wizard",
            action=action,
            reference_image=base_character,
            clean_up=nano_banana_key is not None
        )

        # Create sprite sheet
        client.create_sprite_sheet(frames, f"wizard_{action}", columns=4)

    # Test Nano Banana cleanup if available
    if nano_banana_key:
        print("\n4. Testing Nano Banana cleanup workflow...")
        cleaner = NanoBananaPixelArtCleaner(nano_banana_key)

        # Clean some character images
        characters_dir = Path("assets/pixellab/characters")
        character_files = list(characters_dir.glob("*.png"))

        for i, char_file in enumerate(character_files[:2]):  # Clean first 2
            print(f"   Cleaning character {i+1}: {char_file.name}")

            # Load and clean with different enhancement types
            from PIL import Image
            image = Image.open(char_file)

            for enhancement_type in ["character", "game_ready"]:
                cleaned = cleaner.clean_pixel_art(
                    image,
                    char_file.stem.replace('_', ' '),
                    enhancement_type
                )

                if cleaned:
                    cleaned_path = Path("assets/pixellab/cleaned") / f"{char_file.stem}_{enhancement_type}_cleaned.png"
                    cleaned_path.parent.mkdir(exist_ok=True)
                    cleaned.save(cleaned_path)
                    print(f"     ✅ {enhancement_type} version saved")

    # Show file structure
    print("\n5. File Structure Created:")
    print("=" * 40)

    def show_tree(directory, prefix=""):
        """Show directory tree structure."""
        items = sorted(directory.iterdir())
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir() and not item.name.startswith('.'):
                next_prefix = prefix + ("    " if is_last else "│   ")
                show_tree(item, next_prefix)

    assets_dir = Path("game_assets")
    if assets_dir.exists():
        show_tree(assets_dir)

    # Count files
    total_files = len(list(assets_dir.rglob("*.png")))
    print(f"\n📊 Total files generated: {total_files}")

    print("\n✅ Complete workflow test finished!")
    print("\n🎯 What you can do now:")
    print("   • Check game_assets/ for organized files")
    print("   • Use NANO_BANANA_CLEANED images for your game")
    print("   • Import sprite sheets into game engines")
    print("   • Generate more assets as needed")
    print("   • Files are timestamped and clearly labeled")

if __name__ == "__main__":
    test_complete_workflow()
