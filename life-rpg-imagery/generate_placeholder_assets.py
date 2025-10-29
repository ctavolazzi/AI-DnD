#!/usr/bin/env python3
"""
Life RPG Placeholder Asset Generator

Generates placeholder imagery for the Life RPG prototype.
Since the PixelLab API key is unavailable, this creates simple
colored placeholder images with text labels.
"""

from pathlib import Path
from datetime import datetime
import json
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = Path(__file__).parent / "generated"
OUTPUT_DIR.mkdir(exist_ok=True)

# Color schemes for different categories
COLORS = {
    "achievements": "#FFD700",  # Gold
    "quests": "#4FC3F7",        # Cyan
    "stats": "#66BB6A",         # Green
    "characters": "#AB47BC",    # Purple
    "ui": "#FF7043"             # Orange
}

def create_placeholder_image(text, category, size=(64, 64)):
    """Create a simple placeholder image with text"""
    img = Image.new('RGBA', size, color=(40, 44, 52, 255))
    draw = ImageDraw.Draw(img)

    # Draw border
    color = COLORS[category]
    border_width = 3
    draw.rectangle([0, 0, size[0]-1, size[1]-1], outline=color, width=border_width)

    # Draw background with category color (semi-transparent)
    r, g, b = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    draw.rectangle([border_width, border_width, size[0]-border_width-1, size[1]-border_width-1],
                   fill=(r, g, b, 80))

    # Draw text
    try:
        # Try to use a nice font
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    except:
        # Fallback to default font
        font = ImageFont.load_default()

    # Wrap text if needed
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] < size[0] - 10:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    # Center text
    y = (size[1] - len(lines) * 12) // 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (size[0] - text_width) // 2
        draw.text((x, y), line, fill='white', font=font)
        y += 12

    return img

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

def generate_achievements():
    """Generate achievement badge placeholders"""
    print("\n🏆 Generating Achievement Badges...")

    achievements = [
        ("First Dollar", "Earned your first dollar from content"),
        ("The Flipper", "Completed first furniture flip"),
        ("Consistent Creator", "Posted daily for 7 days"),
        ("Four Figures", "Saved $1,000"),
        ("Ten Grand", "Hit $10K in land fund"),
        ("Workshop Dreamer", "Created detailed workshop plan"),
        ("Custom Creator", "Completed first custom commission"),
        ("YouTube Partner", "Achieved monetization"),
        ("Landowner", "Purchased your land"),
        ("Boss Mode", "Hired your first employee")
    ]

    generated = []
    for name, description in achievements:
        image = create_placeholder_image(name, "achievements")
        metadata = save_image(image, "achievements", name, description)
        generated.append(metadata)

    return generated

def generate_quest_icons():
    """Generate quest line themed icons"""
    print("\n🎯 Generating Quest Line Icons...")

    quests = [
        ("Van Life", "Van Down By The River quest line"),
        ("Land Fund", "The Land Fund quest line"),
        ("Workshop Path", "Building the Workshop quest line"),
        ("Content Empire", "Content Empire quest line"),
        ("Business Builder", "Business Empire quest line"),
    ]

    generated = []
    for name, description in quests:
        image = create_placeholder_image(name, "quests")
        metadata = save_image(image, "quests", name, description)
        generated.append(metadata)

    return generated

def generate_stat_icons():
    """Generate stat and UI icons"""
    print("\n📊 Generating Stat Icons...")

    stats = [
        ("Cash", "Cash on hand"),
        ("Land Fund", "Land fund savings"),
        ("Content Pieces", "Content pieces created"),
        ("Restorations", "Restoration projects completed"),
        ("Skills", "Skills learned"),
        ("Connections", "Connections made"),
        ("Level Up", "Level up effect"),
        ("XP Gain", "XP gain indicator"),
    ]

    generated = []
    for name, description in stats:
        image = create_placeholder_image(name, "stats")
        metadata = save_image(image, "stats", name, description)
        generated.append(metadata)

    return generated

def generate_character_sprites():
    """Generate main character sprites for the Life RPG"""
    print("\n👤 Generating Character Sprites...")

    characters = [
        ("Protagonist Front", "Main character front view"),
        ("Protagonist Side", "Main character side view"),
        ("Van Asset", "Player's van home"),
        ("Workshop Building", "Workshop location"),
    ]

    generated = []
    for name, description in characters:
        image = create_placeholder_image(name, "characters", size=(128, 128))
        metadata = save_image(image, "characters", name, description)
        generated.append(metadata)

    return generated

def generate_ui_elements():
    """Generate UI elements and decorative assets"""
    print("\n🎨 Generating UI Elements...")

    ui_elements = [
        ("Trophy Gold", "Achievement trophy"),
        ("Trophy Silver", "Second place trophy"),
        ("Trophy Bronze", "Third place trophy"),
        ("Quest Complete", "Quest completion banner"),
        ("Daily Streak", "Daily streak indicator"),
        ("Money Bag", "Money bag icon"),
    ]

    generated = []
    for name, description in ui_elements:
        image = create_placeholder_image(name, "ui")
        metadata = save_image(image, "ui", name, description)
        generated.append(metadata)

    return generated

def main():
    """Main generation pipeline"""
    print("=" * 60)
    print("LIFE RPG PLACEHOLDER ASSET GENERATOR")
    print("=" * 60)
    print(f"Output Directory: {OUTPUT_DIR}")
    print("=" * 60)

    # Generate all asset categories
    all_generated = {
        "achievements": generate_achievements(),
        "quests": generate_quest_icons(),
        "stats": generate_stat_icons(),
        "characters": generate_character_sprites(),
        "ui": generate_ui_elements()
    }

    # Save metadata
    metadata_file = OUTPUT_DIR / "metadata.json"
    with open(metadata_file, 'w') as f:
        json.dump({
            "generated_at": datetime.now().isoformat(),
            "total_images": sum(len(v) for v in all_generated.values()),
            "note": "These are placeholder images. Replace with actual pixel art when API key is available.",
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
    print("\nNote: These are placeholder images.")
    print("Replace with actual pixel art when PixelLab API key is available.")

if __name__ == "__main__":
    main()
