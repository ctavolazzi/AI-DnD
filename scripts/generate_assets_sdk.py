#!/usr/bin/env python3
"""
Asset Generation Script (SDK Version)

Uses the PixelLab Python SDK for direct API access.

Usage:
    python scripts/generate_assets_sdk.py
    
Environment:
    PIXELLAB_API_KEY    Your PixelLab API token
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Check for SDK
try:
    import pixellab
    print("✅ PixelLab SDK loaded")
except ImportError:
    print("❌ PixelLab SDK not installed. Run: pip install pixellab")
    sys.exit(1)


def main():
    # Get API key
    api_key = os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        # Try loading from .env
        env_file = project_root / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("PIXELLAB_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ Error: PIXELLAB_API_KEY not found")
        print("\nSet it with:")
        print("  export PIXELLAB_API_KEY='your-api-key'")
        sys.exit(1)
    
    print("🎨 PixelLab SDK Asset Generator")
    print("=" * 50)
    
    try:
        client = pixellab.Client(secret=api_key)
        print("✅ Connected to PixelLab\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    # Create output directory
    output_dir = project_root / "game_assets" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate a test image using pixflux
    print("🖼️  Generating test image...")
    try:
        response = client.generate_image_pixflux(
            description="brave knight with silver armor, blue cape, pixel art character",
            image_size={"width": 64, "height": 64},
            detail="highly detailed",
            outline="single color black outline"
        )
        
        # Save the image
        if hasattr(response, 'image') and response.image:
            if hasattr(response.image, 'pil_image'):
                pil_img = response.image.pil_image()
                save_path = output_dir / "test_knight.png"
                pil_img.save(str(save_path))
                print(f"✅ Saved: {save_path}")
            elif hasattr(response.image, 'base64'):
                import base64
                raw = base64.b64decode(response.image.base64)
                save_path = output_dir / "test_knight.png"
                save_path.write_bytes(raw)
                print(f"✅ Saved: {save_path}")
            else:
                print("⚠️  Unknown image format")
        else:
            print("⚠️  No image in response")
            
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        print(f"   Error type: {type(e).__name__}")
    
    # Generate item icons
    print("\n🗡️  Generating item icons...")
    items = [
        ("sword", "golden sword with gems, pixel art icon"),
        ("shield", "round wooden shield, pixel art icon"),
        ("potion", "red health potion bottle, pixel art icon"),
    ]
    
    for item_name, description in items:
        try:
            response = client.generate_image_pixflux(
                description=description,
                image_size={"width": 32, "height": 32},
                detail="medium detail",
                no_background=True
            )
            
            if hasattr(response, 'image') and response.image:
                if hasattr(response.image, 'pil_image'):
                    pil_img = response.image.pil_image()
                    save_path = output_dir / f"item_{item_name}.png"
                    pil_img.save(str(save_path))
                    print(f"  ✅ {item_name}: {save_path}")
                elif hasattr(response.image, 'base64'):
                    import base64
                    raw = base64.b64decode(response.image.base64)
                    save_path = output_dir / f"item_{item_name}.png"
                    save_path.write_bytes(raw)
                    print(f"  ✅ {item_name}: {save_path}")
        except Exception as e:
            print(f"  ❌ {item_name} failed: {e}")
    
    # Generate scene background
    print("\n🏰 Generating scene...")
    try:
        response = client.generate_image_pixflux(
            description="dark dungeon interior with torches, stone walls, pixel art background",
            image_size={"width": 256, "height": 192},
            detail="highly detailed"
        )
        
        if hasattr(response, 'image') and response.image:
            if hasattr(response.image, 'pil_image'):
                pil_img = response.image.pil_image()
                save_path = output_dir / "scene_dungeon.png"
                pil_img.save(str(save_path))
                print(f"✅ Saved: {save_path}")
            elif hasattr(response.image, 'base64'):
                import base64
                raw = base64.b64decode(response.image.base64)
                save_path = output_dir / "scene_dungeon.png"
                save_path.write_bytes(raw)
                print(f"✅ Saved: {save_path}")
    except Exception as e:
        print(f"❌ Scene generation failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📁 Assets saved to: {output_dir}")
    print("\n✨ Generation complete!")
    
    # List generated files
    files = list(output_dir.glob("*.png"))
    if files:
        print(f"\nGenerated {len(files)} files:")
        for f in files:
            print(f"  - {f.name}")


if __name__ == "__main__":
    main()

