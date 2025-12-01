#!/usr/bin/env python3
"""
Asset Generation Script

Generates pixel art assets using PixelLab's MCP API.
Run this to create game assets (characters, tilesets, etc.)

Usage:
    python scripts/generate_assets.py [--wait]
    
Options:
    --wait    Wait for all assets to complete (may take 5-10 minutes)

Environment:
    PIXELLAB_API_KEY    Your PixelLab API token
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pygame_mvp.services.pixellab_mcp import (
    PixelLabMCPClient,
    JobStatus,
    generate_game_assets
)


def main():
    parser = argparse.ArgumentParser(description="Generate game assets with PixelLab")
    parser.add_argument("--wait", action="store_true", help="Wait for completion")
    parser.add_argument("--hero-only", action="store_true", help="Only generate hero character")
    parser.add_argument("--tileset-only", action="store_true", help="Only generate tilesets")
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export PIXELLAB_API_KEY='your-api-key'")
        print("\nOr add to .env file")
        sys.exit(1)
    
    print("🎨 PixelLab Asset Generator")
    print("=" * 50)
    
    try:
        client = PixelLabMCPClient(api_key)
        print("✅ Connected to PixelLab API\n")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    jobs = {"characters": [], "tilesets": []}
    
    # Generate characters
    if not args.tileset_only:
        print("🦸 Creating Characters...")
        print("-" * 30)
        
        # Hero
        print("  → Hero Knight...")
        hero = client.create_character(
            description="brave knight with shining silver armor, blue cape, and golden sword",
            name="Hero",
            n_directions=8,
            size=48,
            proportions="heroic"
        )
        if hero.character_id:
            jobs["characters"].append({"name": "hero", "job": hero})
            client.animate_character(hero.character_id, "idle", "standing vigilant")
            client.animate_character(hero.character_id, "walk", "walking confidently")
            client.animate_character(hero.character_id, "attack", "powerful sword swing")
            print(f"    ✅ ID: {hero.character_id}")
        else:
            print(f"    ❌ Failed: {hero.error}")
        
        if not args.hero_only:
            # Goblin
            print("  → Goblin...")
            goblin = client.create_character(
                description="small green goblin with pointy ears, tattered brown clothes, rusty dagger",
                name="Goblin",
                n_directions=4,
                size=32,
                proportions="chibi"
            )
            if goblin.character_id:
                jobs["characters"].append({"name": "goblin", "job": goblin})
                client.animate_character(goblin.character_id, "idle")
                client.animate_character(goblin.character_id, "walk")
                print(f"    ✅ ID: {goblin.character_id}")
            else:
                print(f"    ❌ Failed: {goblin.error}")
            
            # Skeleton
            print("  → Skeleton Warrior...")
            skeleton = client.create_character(
                description="animated skeleton warrior with rusty sword and cracked shield, glowing red eyes",
                name="Skeleton",
                n_directions=4,
                size=48
            )
            if skeleton.character_id:
                jobs["characters"].append({"name": "skeleton", "job": skeleton})
                client.animate_character(skeleton.character_id, "idle")
                client.animate_character(skeleton.character_id, "walk")
                client.animate_character(skeleton.character_id, "attack")
                print(f"    ✅ ID: {skeleton.character_id}")
            else:
                print(f"    ❌ Failed: {skeleton.error}")
            
            # Wizard NPC
            print("  → Wizard NPC...")
            wizard = client.create_character(
                description="elderly wizard with long white beard, blue starry robe, wooden staff with crystal",
                name="Wizard",
                n_directions=4,
                size=48,
                proportions="stylized"
            )
            if wizard.character_id:
                jobs["characters"].append({"name": "wizard", "job": wizard})
                client.animate_character(wizard.character_id, "idle", "stroking beard thoughtfully")
                client.animate_character(wizard.character_id, "cast", "channeling magical energy")
                print(f"    ✅ ID: {wizard.character_id}")
            else:
                print(f"    ❌ Failed: {wizard.error}")
        
        print()
    
    # Generate tilesets
    if not args.hero_only:
        print("🏰 Creating Tilesets...")
        print("-" * 30)
        
        # Dungeon tileset
        print("  → Dungeon Floor + Walls...")
        dungeon = client.create_topdown_tileset(
            lower_description="dark stone dungeon floor with cracks",
            upper_description="stone brick wall with moss",
            tile_size=32,
            transition_size=0.25
        )
        if dungeon.tileset_id:
            jobs["tilesets"].append({"name": "dungeon", "job": dungeon})
            print(f"    ✅ ID: {dungeon.tileset_id}")
        else:
            print(f"    ❌ Failed: {dungeon.error}")
        
        # Forest tileset
        print("  → Forest Grass + Path...")
        forest = client.create_topdown_tileset(
            lower_description="lush green grass with small flowers",
            upper_description="dirt path with pebbles",
            tile_size=32,
            transition_size=0.3
        )
        if forest.tileset_id:
            jobs["tilesets"].append({"name": "forest", "job": forest})
            print(f"    ✅ ID: {forest.tileset_id}")
        else:
            print(f"    ❌ Failed: {forest.error}")
        
        # Tavern tileset
        print("  → Tavern Wood Floor...")
        tavern = client.create_topdown_tileset(
            lower_description="worn wooden tavern floorboards",
            upper_description="stone fireplace tiles",
            tile_size=32,
            transition_size=0.2
        )
        if tavern.tileset_id:
            jobs["tilesets"].append({"name": "tavern", "job": tavern})
            print(f"    ✅ ID: {tavern.tileset_id}")
        else:
            print(f"    ❌ Failed: {tavern.error}")
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 Summary")
    print(f"  Characters submitted: {len(jobs['characters'])}")
    print(f"  Tilesets submitted: {len(jobs['tilesets'])}")
    print()
    
    if jobs["characters"]:
        print("Character IDs (save these!):")
        for char in jobs["characters"]:
            print(f"  {char['name']}: {char['job'].character_id}")
    
    if jobs["tilesets"]:
        print("\nTileset IDs (save these!):")
        for ts in jobs["tilesets"]:
            print(f"  {ts['name']}: {ts['job'].tileset_id}")
    
    print("\n⏳ Processing will take 2-5 minutes per asset")
    print("   Run with --wait to wait for completion")
    
    # Wait for completion if requested
    if args.wait:
        print("\n🕐 Waiting for assets to complete...")
        
        for char in jobs["characters"]:
            print(f"\nWaiting for {char['name']}...")
            result = client.wait_for_character(char["job"].character_id)
            if result.status == JobStatus.COMPLETED:
                print(f"  ✅ {char['name']} ready!")
                if result.download_url:
                    print(f"     Download: {result.download_url}")
            else:
                print(f"  ❌ {char['name']} failed: {result.error}")
        
        for ts in jobs["tilesets"]:
            print(f"\nWaiting for {ts['name']} tileset...")
            result = client.wait_for_tileset(ts["job"].tileset_id)
            if result.status == JobStatus.COMPLETED:
                print(f"  ✅ {ts['name']} ready!")
                if result.download_url:
                    print(f"     Download: {result.download_url}")
            else:
                print(f"  ❌ {ts['name']} failed: {result.error}")
        
        print("\n✨ Asset generation complete!")
    
    # Save job IDs for later retrieval
    job_file = project_root / "game_assets" / "pending_jobs.json"
    job_file.parent.mkdir(exist_ok=True)
    
    import json
    job_data = {
        "characters": [
            {"name": c["name"], "id": c["job"].character_id}
            for c in jobs["characters"] if c["job"].character_id
        ],
        "tilesets": [
            {"name": t["name"], "id": t["job"].tileset_id}
            for t in jobs["tilesets"] if t["job"].tileset_id
        ]
    }
    job_file.write_text(json.dumps(job_data, indent=2))
    print(f"\n📝 Job IDs saved to: {job_file}")


if __name__ == "__main__":
    main()

