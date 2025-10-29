#!/usr/bin/env python3
"""
Test Enhanced PixelLab Client with Improved File Structure
Demonstrates the new project root folder structure and clear file naming
"""

import os
from pathlib import Path
from enhanced_pixellab_client import EnhancedPixelLabClient

def test_improved_workflow():
    """Test the improved workflow with better file organization."""
    print("🎨 Enhanced PixelLab Client - Improved Workflow Test")
    print("=" * 60)

    # Check for API keys
    pixellab_key = os.getenv("PIXELLAB_API_KEY")
    nano_banana_key = os.getenv("GEMINI_API_KEY")

    if not pixellab_key:
        print("❌ PIXELLAB_API_KEY not found")
        print("   Set it with: export PIXELLAB_API_KEY=your_key_here")
        return

    if not nano_banana_key:
        print("⚠️  GEMINI_API_KEY not found - will test without Nano Banana cleanup")
        print("   Set it with: export GEMINI_API_KEY=your_key_here")

    # Initialize enhanced client
    print("\n1. Initializing Enhanced Client...")
    client = EnhancedPixelLabClient(
        api_key=pixellab_key,
        nano_banana_api_key=nano_banana_key
    )

    # Check balance
    balance = client.get_balance()
    print(f"   PixelLab balance: ${balance['credits']} USD")

    # Test character generation with clear naming
    print("\n2. Generating characters with improved naming...")

    test_characters = [
        ("fantasy wizard with staff", "pixflux"),
        ("medieval knight with sword", "bitforge")
    ]

    for description, style in test_characters:
        print(f"\n   Generating: {description} ({style})")
        character = client.generate_character(
            description=description,
            style=style,
            clean_up=nano_banana_key is not None
        )

    # Test animation generation
    print("\n3. Generating animation with clear naming...")

    # Use the first character for animation
    base_character = client.generate_character(
        description="fantasy warrior",
        style="pixflux"
    )

    print("\n   Generating walk animation...")
    walk_frames = client.generate_animation(
        description="fantasy warrior",
        action="walk",
        reference_image=base_character,
        clean_up=nano_banana_key is not None
    )

    # Create sprite sheet
    print("\n4. Creating sprite sheet...")
    client.create_sprite_sheet(walk_frames, "warrior_walk", columns=4)

    # Show the new file structure
    print("\n5. New File Structure in Project Root:")
    print("=" * 50)

    def show_tree(directory, prefix="", max_depth=3, current_depth=0):
        """Show directory tree structure with depth limit."""
        if current_depth >= max_depth:
            return

        try:
            items = sorted(directory.iterdir())
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")

                if item.is_dir() and not item.name.startswith('.') and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    show_tree(item, next_prefix, max_depth, current_depth + 1)
        except PermissionError:
            pass

    game_assets_dir = Path("game_assets")
    if game_assets_dir.exists():
        show_tree(game_assets_dir)

    # Count files and show naming examples
    print(f"\n📊 File Organization Summary:")
    print("=" * 30)

    total_files = len(list(game_assets_dir.rglob("*.png")))
    print(f"Total PNG files: {total_files}")

    # Show naming examples
    print(f"\n📝 File Naming Examples:")
    print("=" * 25)

    characters = list(game_assets_dir.glob("characters/*.png"))
    if characters:
        print("Characters:")
        for char in characters[:2]:  # Show first 2
            print(f"  • {char.name}")

    animations = list(game_assets_dir.glob("animations/*/*.png"))
    if animations:
        print("Animations:")
        for anim in animations[:2]:  # Show first 2
            print(f"  • {anim.name}")

    cleaned = list(game_assets_dir.glob("cleaned/*/*.png"))
    if cleaned:
        print("Nano Banana Cleaned:")
        for clean in cleaned[:2]:  # Show first 2
            print(f"  • {clean.name}")

    print(f"\n✅ Improved workflow test completed!")
    print(f"\n🎯 Key Improvements:")
    print("   • Files saved to game_assets/ in project root")
    print("   • Timestamps in all filenames (YYYYMMDD_HHMMSS)")
    print("   • NANO_BANANA_CLEANED clearly marked in filenames")
    print("   • Organized by type: characters/, animations/, cleaned/")
    print("   • Ready for game development workflow")

if __name__ == "__main__":
    test_improved_workflow()
