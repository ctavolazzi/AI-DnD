#!/usr/bin/env python3
"""Generate a complete illustrated D&D adventure with AI-generated images."""

import os
import requests
import json
import base64
from pathlib import Path

print("🎨 Generating Complete Illustrated Adventure")
print("="*70 + "\n")

# Create output directory
output_dir = Path("illustrated_adventure")
output_dir.mkdir(exist_ok=True)

# Load the character we created earlier
with open('complete_adventure.json', 'r') as f:
    adventure_data = json.load(f)

character = adventure_data['character']
quest = adventure_data['quest']
opening_scene = adventure_data['opening_scene']

print("📖 Adventure: Lyra Stormblade's Quest")
print("="*70 + "\n")

# Scene descriptions for image generation
scenes = [
    {
        "title": "Character Portrait",
        "description": "Portrait of Lyra Stormblade, a young female Aasimar Paladin with celestial features. She has silver hair, glowing eyes, and wears shining plate armor with a holy symbol of Pelor. Divine light emanates from her. Fantasy character art, detailed, heroic pose.",
        "filename": "01_lyra_portrait.png"
    },
    {
        "title": "The Monastery Ruins",
        "description": "Ruins of the Silverpeak Mountains monastery at sunset. Destroyed stone buildings with sacred flame symbols, bodies of fallen monks, ash and smoke in the air. Dramatic lighting, somber mood, fantasy landscape art.",
        "filename": "02_monastery_ruins.png"
    },
    {
        "title": "The Whispering Caves",
        "description": "The entrance to the Whispering Caves in the Dragon's Tooth mountains. A dark, foreboding cave mouth carved into jagged peaks. Thunder clouds overhead, ominous atmosphere. Ancient spirits visible as wisps. Epic fantasy environment art.",
        "filename": "03_whispering_caves.png"
    },
    {
        "title": "The Corrupted Sunstone",
        "description": "A powerful magical artifact called the Sunstone, glowing with corrupted dark and light energy. The relic pulses with demonic power, held by a gnoll Flind with glowing malevolent eyes. Dark fantasy art, ominous magical lighting.",
        "filename": "04_corrupted_sunstone.png"
    }
]

print(f"Generating {len(scenes)} illustrated scenes...\n")

generated_images = []

for i, scene in enumerate(scenes, 1):
    print(f"{i}/{len(scenes)} - {scene['title']}...")
    print(f"   Prompt: {scene['description'][:60]}...")

    try:
        response = requests.post(
            "http://localhost:5000/generate-scene",
            json={"description": scene['description']},
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            image_data = result['image']

            # Extract base64
            if image_data.startswith('data:image'):
                base64_data = image_data.split(',')[1]
            else:
                base64_data = image_data

            # Save image
            image_bytes = base64.b64decode(base64_data)
            filepath = output_dir / scene['filename']
            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            size_kb = len(image_bytes) / 1024
            print(f"   ✅ Saved ({size_kb:.1f} KB): {filepath}")

            generated_images.append({
                "title": scene['title'],
                "filename": scene['filename'],
                "path": str(filepath),
                "size_kb": size_kb
            })

        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

print("\n" + "="*70)
print("✨ Creating Adventure Document")
print("="*70 + "\n")

# Create HTML adventure document
html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Quest of Lyra Stormblade</title>
    <style>
        body {{
            font-family: 'Georgia', serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #1a1a1a;
            color: #e0e0e0;
            line-height: 1.8;
        }}
        h1 {{
            color: #ffd700;
            text-align: center;
            font-size: 2.5em;
            margin: 40px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }}
        h2 {{
            color: #c4a000;
            border-bottom: 2px solid #444;
            padding-bottom: 10px;
            margin-top: 40px;
        }}
        .image-container {{
            text-align: center;
            margin: 30px 0;
        }}
        .image-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}
        .caption {{
            font-style: italic;
            color: #aaa;
            margin-top: 10px;
        }}
        .stats {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #ffd700;
            margin: 20px 0;
        }}
        .scene-text {{
            background: #252525;
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 1.1em;
            font-family: 'Palatino', serif;
        }}
    </style>
</head>
<body>
    <h1>⚔️ The Quest of Lyra Stormblade ⚔️</h1>

    <div class="image-container">
        <img src="{generated_images[0]['filename'] if len(generated_images) > 0 else ''}" alt="Lyra Stormblade">
        <div class="caption">Lyra Stormblade, Aasimar Paladin of Pelor</div>
    </div>

    <h2>The Champion</h2>
    <div class="stats">
        <pre>{character[:800]}...</pre>
    </div>

    <h2>The Monastery Falls</h2>
    <div class="scene-text">
        The air crackled with the stench of blood and burnt incense. The monastery, once a beacon of light,
        lay in ruins. The monks who raised Lyra were gone, and the sacred Sunstone stolen by demonic gnolls...
    </div>

    <div class="image-container">
        <img src="{generated_images[1]['filename'] if len(generated_images) > 1 else ''}" alt="Monastery Ruins">
        <div class="caption">The ruins of the Silverpeak monastery</div>
    </div>

    <h2>The Quest</h2>
    <div class="stats">
        {quest}
    </div>

    <h2>Into the Whispering Caves</h2>
    <div class="scene-text">
        {opening_scene}
    </div>

    <div class="image-container">
        <img src="{generated_images[2]['filename'] if len(generated_images) > 2 else ''}" alt="Whispering Caves">
        <div class="caption">The entrance to the Whispering Caves</div>
    </div>

    <h2>The Corrupted Relic</h2>
    <div class="scene-text">
        Deep within the caves, the Sunstone pulses with corrupted power. The gnoll Flind prepares the ritual
        to summon a demon lord. Time is running out. Lyra must act now or lose everything...
    </div>

    <div class="image-container">
        <img src="{generated_images[3]['filename'] if len(generated_images) > 3 else ''}" alt="The Sunstone">
        <div class="caption">The corrupted Sunstone</div>
    </div>

    <h2>To Be Continued...</h2>
    <div class="scene-text">
        Will Lyra recover the Sunstone? Can she stop the demon lord's summoning?
        The fate of the realm hangs in the balance...
    </div>

    <div style="text-align: center; margin: 60px 0 20px 0; color: #888;">
        <p>🎲 Generated with AI-DnD • Powered by Gemini 2.0 Flash 🎲</p>
    </div>
</body>
</html>
"""

html_path = output_dir / "adventure.html"
with open(html_path, 'w') as f:
    f.write(html_content)

print(f"✅ Adventure document created: {html_path}")
print(f"\n🌟 Generated {len(generated_images)} images")
print("\nOpen the adventure:")
print(f"   open {html_path}")
print("\n" + "="*70)
print("🎉 ILLUSTRATED ADVENTURE COMPLETE!")
print("="*70)

# Open the adventure automatically
import subprocess
subprocess.run(['open', str(html_path)])
