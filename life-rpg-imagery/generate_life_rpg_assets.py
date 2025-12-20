#!/usr/bin/env python3
"""
Life RPG Asset Generator

Generates pixel art imagery for the Life RPG prototype using PixelLab API.
This creates achievement badges, quest icons, stat icons, and other UI elements.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path to import pixellab_integration
sys.path.insert(0, str(Path(__file__).parent.parent))

from pixellab_integration.pixellab_client import PixelLabClient

# PixelLab API Configuration
API_KEY = os.getenv("PIXELLAB_API_KEY")
if not API_KEY:
    raise ValueError("PIXELLAB_API_KEY environment variable not set")
OUTPUT_DIR = Path(__file__).parent / "generated"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

def save_image(image, category, name, description):
    """Save image and track metadata"""
    category_dir = OUTPUT_DIR / category
    category_dir.mkdir(exist_ok=True)

    filename = f"{name.lower().replace(' ', '_')}.png"
    filepath = category_dir / filename

    image.save(str(filepath))
    print(f"✓ Generated: {category}/{filename}")

    return {
        "name": name,
        "description": description,
        "category": category,
        "filename": filename,
        "path": str(filepath.relative_to(OUTPUT_DIR.parent)),
        "timestamp": datetime.now().isoformat()
    }

def generate_achievements(client):
    """Generate achievement badge pixel art"""
    print("\n🏆 Generating Achievement Badges...")

    achievements = [
        ("First Dollar", "golden dollar coin with sparkles, pixel art icon, isometric", "Earned your first dollar from content"),
        ("The Flipper", "restored vintage furniture piece, pixel art icon, before and after split", "Completed first furniture flip"),
        ("Consistent Creator", "calendar with checkmarks, pixel art icon, streak symbols", "Posted daily for 7 days"),
        ("Four Figures", "stack of money bills, pixel art icon, glowing $1000", "Saved $1,000"),
        ("Ten Grand", "large money bag with $10K label, pixel art icon, heavy and full", "Hit $10K in land fund"),
        ("Workshop Dreamer", "blueprint scroll with tools, pixel art icon, planning theme", "Created detailed workshop plan"),
        ("Custom Creator", "custom made item with commission tag, pixel art icon, handcrafted", "Completed first custom commission"),
        ("YouTube Partner", "play button trophy, pixel art icon, silver and red", "Achieved monetization"),
        ("Landowner", "land deed document with signature, pixel art icon, official and framed", "Purchased your land"),
        ("Boss Mode", "business person silhouette with handshake, pixel art icon, professional", "Hired your first employee")
    ]

    generated = []
    for name, prompt, description in achievements:
        try:
            image = client.generate_character(
                description=prompt,
                width=64,
                height=64,
                outline='thick',
                shading='smooth',
                no_background=True,
                view='front'
            )
            metadata = save_image(image, "achievements", name, description)
            generated.append(metadata)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

    return generated

def generate_quest_icons(client):
    """Generate quest line themed icons"""
    print("\n🎯 Generating Quest Line Icons...")

    quests = [
        ("Van Life", "camping van parked by river, pixel art icon, cozy and mobile", "Van Down By The River quest line"),
        ("Land Fund", "piggy bank with land in background, pixel art icon, saving theme", "The Land Fund quest line"),
        ("Workshop Path", "workshop building with tools, pixel art icon, craftsman space", "Building the Workshop quest line"),
        ("Content Empire", "camera and content creation setup, pixel art icon, creative space", "Content Empire quest line"),
        ("Business Builder", "office building with growth arrow, pixel art icon, empire theme", "Business Empire quest line"),
    ]

    generated = []
    for name, prompt, description in quests:
        try:
            image = client.generate_character(
                description=prompt,
                width=64,
                height=64,
                outline='thick',
                shading='smooth',
                no_background=True,
                view='front'
            )
            metadata = save_image(image, "quests", name, description)
            generated.append(metadata)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

    return generated

def generate_stat_icons(client):
    """Generate stat and UI icons"""
    print("\n📊 Generating Stat Icons...")

    stats = [
        ("Cash", "stack of dollar bills, pixel art icon, green money", "Cash on hand"),
        ("Land Fund", "treasure chest with land deed, pixel art icon, savings theme", "Land fund savings"),
        ("Content Pieces", "video camera with play symbol, pixel art icon, content creation", "Content pieces created"),
        ("Restorations", "furniture restoration tools, pixel art icon, craftsman theme", "Restoration projects completed"),
        ("Skills", "skill tree with glowing nodes, pixel art icon, learning theme", "Skills learned"),
        ("Connections", "network of people connected, pixel art icon, community theme", "Connections made"),
        ("Level Up", "star burst with up arrow, pixel art icon, bright and exciting", "Level up effect"),
        ("XP Gain", "experience orb glowing, pixel art icon, progress theme", "XP gain indicator"),
    ]

    generated = []
    for name, prompt, description in stats:
        try:
            image = client.generate_character(
                description=prompt,
                width=64,
                height=64,
                outline='thick',
                shading='smooth',
                no_background=True,
                view='front'
            )
            metadata = save_image(image, "stats", name, description)
            generated.append(metadata)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

    return generated

def generate_character_sprites(client):
    """Generate main character sprites for the Life RPG"""
    print("\n👤 Generating Character Sprites...")

    characters = [
        ("Protagonist Front", "young entrepreneur character, casual clothes, pixel art character, front view, confident", "Main character front view"),
        ("Protagonist Side", "young entrepreneur character, casual clothes, pixel art character, side view, walking", "Main character side view"),
        ("Van Asset", "retro camping van, pixel art vehicle, side view, detailed", "Player's van home"),
        ("Workshop Building", "small workshop building, pixel art building, front view, craftsman theme", "Workshop location"),
    ]

    generated = []
    for name, prompt, description in characters:
        try:
            image = client.generate_character(
                description=prompt,
                width=128,
                height=128,
                outline='thick',
                shading='smooth',
                no_background=True,
                view='front'
            )
            metadata = save_image(image, "characters", name, description)
            generated.append(metadata)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

    return generated

def generate_ui_elements(client):
    """Generate UI elements and decorative assets"""
    print("\n🎨 Generating UI Elements...")

    ui_elements = [
        ("Trophy Gold", "golden trophy cup, pixel art icon, shiny and award-winning", "Achievement trophy"),
        ("Trophy Silver", "silver trophy cup, pixel art icon, polished and prestigious", "Second place trophy"),
        ("Trophy Bronze", "bronze trophy cup, pixel art icon, solid achievement", "Third place trophy"),
        ("Quest Complete", "quest scroll with checkmark, pixel art icon, completed quest", "Quest completion banner"),
        ("Daily Streak", "fire icon with numbers, pixel art icon, streak counter", "Daily streak indicator"),
        ("Money Bag", "bulging money bag with dollar sign, pixel art icon, wealth", "Money bag icon"),
    ]

    generated = []
    for name, prompt, description in ui_elements:
        try:
            image = client.generate_character(
                description=prompt,
                width=64,
                height=64,
                outline='thick',
                shading='smooth',
                no_background=True,
                view='front'
            )
            metadata = save_image(image, "ui", name, description)
            generated.append(metadata)
        except Exception as e:
            print(f"✗ Failed to generate {name}: {e}")

    return generated

def main():
    """Main generation pipeline"""
    print("=" * 60)
    print("LIFE RPG ASSET GENERATOR")
    print("=" * 60)
    print(f"Output Directory: {OUTPUT_DIR}")
    print(f"API Key: {API_KEY[:10]}...")
    print("=" * 60)

    # Initialize client
    client = PixelLabClient(api_key=API_KEY)

    # Check balance
    try:
        balance = client.get_balance()
        print(f"\n💰 Current API Balance: {balance.credits} credits")
    except:
        print("\n⚠ Could not check API balance")

    # Generate all asset categories
    all_generated = {
        "achievements": generate_achievements(client),
        "quests": generate_quest_icons(client),
        "stats": generate_stat_icons(client),
        "characters": generate_character_sprites(client),
        "ui": generate_ui_elements(client)
    }

    # Save metadata
    metadata_file = OUTPUT_DIR / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_images": sum(len(v) for v in all_generated.values()),
            "categories": all_generated
        }, f, indent=2)

    print("\n" + "=" * 60)
    print("GENERATION COMPLETE!")
    print("=" * 60)
    print(f"Total Images Generated: {sum(len(v) for v in all_generated.values())}")
    print(f"Metadata saved to: {metadata_file}")
    print("\nCategories:")
    for category, items in all_generated.items():
        print(f"  - {category}: {len(items)} images")
    print("\n✨ Ready to use in Life RPG prototype!")

if __name__ == "__main__":
    main()
