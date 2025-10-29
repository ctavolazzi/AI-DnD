#!/usr/bin/env python3
"""
Nano Banana Cleanup Demo
Demonstrates the cleanup workflow (works without API key for demo)
"""

import os
from pathlib import Path
from PIL import Image, ImageFilter, ImageEnhance
import shutil

def demo_pixel_art_cleanup():
    """Demo the pixel art cleanup process."""
    print("🧹 Nano Banana Pixel Art Cleanup Demo")
    print("=" * 50)

    # Check if we have images to work with
    characters_dir = Path("assets/pixellab/characters")
    if not characters_dir.exists():
        print("❌ No character images found. Run the enhanced client first.")
        return

    # Create cleaned directory
    cleaned_dir = Path("assets/pixellab/cleaned")
    cleaned_dir.mkdir(exist_ok=True)

    # Get some character images
    character_files = list(characters_dir.glob("*.png"))
    if not character_files:
        print("❌ No character images found.")
        return

    print(f"Found {len(character_files)} character images to process")

    # Demo different cleanup techniques
    cleanup_techniques = [
        ("basic", "Basic cleanup - smooth edges and enhance contrast"),
        ("enhanced", "Enhanced cleanup - improve colors and sharpness"),
        ("game_ready", "Game-ready cleanup - optimize for game development")
    ]

    for i, char_file in enumerate(character_files[:3]):  # Process first 3 images
        print(f"\n🎨 Processing: {char_file.name}")

        # Load the image
        image = Image.open(char_file)
        print(f"   Original size: {image.size}, mode: {image.mode}")

        for technique, description in cleanup_techniques:
            print(f"   Applying {technique} cleanup...")

            # Apply different cleanup techniques
            if technique == "basic":
                # Basic cleanup: smooth edges, enhance contrast
                cleaned = image.copy()
                cleaned = cleaned.filter(ImageFilter.SMOOTH_MORE)
                enhancer = ImageEnhance.Contrast(cleaned)
                cleaned = enhancer.enhance(1.2)

            elif technique == "enhanced":
                # Enhanced cleanup: improve colors and sharpness
                cleaned = image.copy()
                cleaned = cleaned.filter(ImageFilter.SHARPEN)
                enhancer = ImageEnhance.Color(cleaned)
                cleaned = enhancer.enhance(1.1)
                enhancer = ImageEnhance.Brightness(cleaned)
                cleaned = enhancer.enhance(1.05)

            elif technique == "game_ready":
                # Game-ready cleanup: optimize for game development
                cleaned = image.copy()
                # Ensure it's RGBA for transparency
                if cleaned.mode != 'RGBA':
                    cleaned = cleaned.convert('RGBA')
                # Apply slight sharpening for crisp edges
                cleaned = cleaned.filter(ImageFilter.SHARPEN)
                # Enhance contrast for better visibility
                enhancer = ImageEnhance.Contrast(cleaned)
                cleaned = enhancer.enhance(1.15)
                # Slightly enhance saturation
                enhancer = ImageEnhance.Color(cleaned)
                cleaned = enhancer.enhance(1.05)

            # Save the cleaned image
            cleaned_filename = f"{char_file.stem}_{technique}_cleaned.png"
            cleaned_path = cleaned_dir / cleaned_filename
            cleaned.save(cleaned_path)
            print(f"     ✅ Saved: {cleaned_path}")

    # Show the results
    print(f"\n📁 Cleanup results saved to: {cleaned_dir}")
    cleaned_files = list(cleaned_dir.glob("*.png"))
    print(f"📊 Generated {len(cleaned_files)} cleaned images")

    # Show file structure
    print("\n📂 Cleaned Images:")
    for file in sorted(cleaned_files):
        print(f"   • {file.name}")

    print("\n✅ Demo completed!")
    print("\n💡 In the real Nano Banana workflow:")
    print("   • Images would be sent to Gemini for AI-powered cleanup")
    print("   • AI would analyze and enhance the pixel art")
    print("   • Results would be more sophisticated than basic filters")
    print("   • Each enhancement type would have specific AI prompts")

def show_workflow_comparison():
    """Show the difference between original and cleaned images."""
    print("\n🔍 Workflow Comparison:")
    print("=" * 30)

    print("1. PixelLab Generation:")
    print("   • AI generates raw pixel art from text description")
    print("   • May have rough edges, inconsistent colors")
    print("   • Good base but needs refinement")

    print("\n2. Nano Banana Cleanup:")
    print("   • AI analyzes the pixel art")
    print("   • Identifies areas for improvement")
    print("   • Enhances colors, edges, and details")
    print("   • Makes it more professional and game-ready")

    print("\n3. Final Result:")
    print("   • Clean, professional pixel art")
    print("   • Consistent style and quality")
    print("   • Ready for game development")
    print("   • Suitable for asset stores")

if __name__ == "__main__":
    demo_pixel_art_cleanup()
    show_workflow_comparison()
