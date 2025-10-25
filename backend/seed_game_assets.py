#!/usr/bin/env python3
"""
Seed FastAPI backend with all game scene images

This script:
1. Connects to FastAPI backend (port 8000)
2. Checks if each scene already exists in database
3. Generates only missing scenes
4. Stores in database + filesystem
5. Images persist forever (survive restarts)

Usage:
    # Make sure backend is running first:
    # uvicorn app.main:app --reload

    python seed_game_assets.py
"""
import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

# All game scenes that need images
GAME_SCENES = [
    {
        "subject_name": "Emberpeak Entrance",
        "prompt": "the entrance to Emberpeak, a mountain village at dawn. Stone archway covered in moss, cobblestone path, misty mountain peaks in background, warm torchlight. Fantasy RPG setting, atmospheric lighting.",
        "location": "village_entrance"
    },
    {
        "subject_name": "Starting Tavern",
        "prompt": "A dimly lit medieval tavern interior with wooden tables, stone fireplace, hanging lanterns, adventurers at the bar. Fantasy RPG setting, cozy atmosphere.",
        "location": "tavern"
    },
    {
        "subject_name": "Town Square",
        "prompt": "A bustling fantasy town square with a marble fountain, market stalls, townspeople, medieval buildings. Bright daylight, lively atmosphere.",
        "location": "town_square"
    },
    {
        "subject_name": "Market District",
        "prompt": "A crowded fantasy marketplace with colorful merchant tents, exotic goods, bustling crowd, hanging banners. Vibrant colors, medieval setting.",
        "location": "market"
    },
    {
        "subject_name": "Temple District",
        "prompt": "A peaceful temple district with stone religious buildings, prayer flags, incense smoke, holy symbols. Serene atmosphere, golden light.",
        "location": "temple"
    },
    {
        "subject_name": "North Gate",
        "prompt": "A fortified castle gate with guard towers, medieval stone walls, armed sentries, mountain path ahead. Imposing architecture, defensive structure.",
        "location": "north_gate"
    },
    {
        "subject_name": "Residential Quarter",
        "prompt": "A quiet medieval residential area with small stone cottages, vegetable gardens, cobblestone paths. Peaceful neighborhood, afternoon light.",
        "location": "residential"
    },
    {
        "subject_name": "Craftsman's Row",
        "prompt": "A medieval street of workshops and forges, blacksmiths hammering, smoke from chimneys, artisan tools. Industrial medieval setting.",
        "location": "craftsman"
    },
    {
        "subject_name": "West Road",
        "prompt": "A dirt road through rolling green hills, wooden signpost, distant mountains, afternoon sunlight. Open landscape, travel route.",
        "location": "west_road"
    },
    {
        "subject_name": "Mine Entrance",
        "prompt": "The dark entrance to mountain mines, wooden support beams, lanterns, mine cart tracks descending. Ominous atmosphere, transition to underground.",
        "location": "mine_entrance"
    },
    {
        "subject_name": "East Bridge",
        "prompt": "A stone bridge crossing a clear river, medieval architecture, forest on both sides, flowing water. Scenic travel location.",
        "location": "east_bridge"
    },
    # Underground locations
    {
        "subject_name": "Shaft Junction",
        "prompt": "An underground mine junction with crossing tunnels, wooden support beams, mine cart tracks, lantern light. Dark underground atmosphere.",
        "location": "shaft_junction"
    },
    {
        "subject_name": "Mining Camp",
        "prompt": "An abandoned mining camp underground, scattered tools and equipment, overturned cart, eerie silence. Mysterious abandoned location.",
        "location": "mining_camp"
    },
    {
        "subject_name": "Crystal Cavern",
        "prompt": "A glowing underground cavern with luminescent purple and blue crystals embedded in walls, magical atmosphere. Beautiful otherworldly scene.",
        "location": "crystal_cavern"
    },
    {
        "subject_name": "Collapsed Tunnel",
        "prompt": "A collapsed mine tunnel blocked by fallen rocks and timber, dust in the air, partial cave-in. Dangerous obstruction.",
        "location": "collapsed_tunnel"
    },
    {
        "subject_name": "Underground River",
        "prompt": "An underground river in a cavern, rushing water, ancient stone bridges, moss-covered rocks, echo. Atmospheric underground water feature.",
        "location": "underground_river"
    },
    {
        "subject_name": "Fungal Grotto",
        "prompt": "A damp underground grotto filled with large bioluminescent mushrooms glowing green and yellow, fungal growth. Alien underground ecosystem.",
        "location": "fungal_grotto"
    },
    {
        "subject_name": "Deep Chamber",
        "prompt": "A vast deep underground chamber with mysterious ancient runes carved into stone walls, magical energy, torchlight. Epic dungeon chamber.",
        "location": "deep_chamber"
    }
]

def check_backend():
    """Check if backend is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_existing(subject_name):
    """Check if image already exists in database"""
    try:
        response = requests.get(
            f"{API_URL}/images/search",
            params={
                "subject_name": subject_name,
                "subject_type": "scene"
            }
        )
        if response.status_code == 200:
            data = response.json()
            return data.get('total', 0) > 0
        return False
    except:
        return False

def generate_scene(scene_data):
    """Generate a new scene image"""
    payload = {
        "subject_type": "scene",
        "subject_name": scene_data["subject_name"],
        "prompt": scene_data["prompt"],
        "aspect_ratio": "16:9",
        "component": "scene-viewer"
    }

    try:
        response = requests.post(
            f"{API_URL}/images/generate",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
            return None

    except requests.exceptions.Timeout:
        print(f"   ❌ Timeout (>30s)")
        return None
    except Exception as e:
        print(f"   ❌ Exception: {str(e)[:100]}")
        return None

def main():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  GAME ASSETS SEEDER (FastAPI Backend)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    # Check backend
    print("Checking backend...")
    if not check_backend():
        print("❌ Backend not running!")
        print("   Start it with: cd backend && uvicorn app.main:app --reload")
        return
    print("✅ Backend is running\n")

    # Seed images
    total = len(GAME_SCENES)
    generated = 0
    cached = 0
    failed = 0

    print(f"📋 Seeding {total} game scenes...\n")
    start_time = time.time()

    for i, scene in enumerate(GAME_SCENES, 1):
        name = scene["subject_name"]
        progress = f"[{i}/{total}]"

        print(f"{progress} {name}...")

        # Check if already exists
        if check_existing(name):
            print(f"   ⚡ Already in database (cache hit #{cached + 1})")
            cached += 1
            continue

        # Generate new image
        result = generate_scene(scene)

        if result:
            file_size_kb = result.get('file_size_bytes', 0) / 1024
            gen_time_ms = result.get('generation_time_ms', 0)
            print(f"   ✅ Generated ({file_size_kb:.1f} KB, {gen_time_ms}ms)")
            generated += 1
        else:
            failed += 1

        # Delay to avoid overwhelming API (2 seconds between requests)
        if i < total:
            time.sleep(2)

    elapsed = time.time() - start_time

    # Summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  SEEDING COMPLETE")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    print(f"✅ Generated:      {generated}")
    print(f"⚡ Already cached: {cached}")
    print(f"❌ Failed:         {failed}")
    print(f"📊 Total:          {total}")
    print(f"⏱️  Time:           {elapsed:.1f}s\n")

    print("💾 Storage:")
    print(f"   Database: backend/dnd_game.db")
    print(f"   Files:    backend/images/\n")

    if failed > 0:
        print("⚠️  Some images failed to generate.")
        print("   Run script again to retry failed images.\n")

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  NEXT STEPS")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("1. Verify images in database:")
    print("   curl http://localhost:8000/api/v1/images/search?subject_type=scene")
    print("\n2. View API docs:")
    print("   open http://localhost:8000/docs")
    print("\n3. Update frontend to use backend API")
    print("   (See MIGRATION_GUIDE.md)")
    print("\n4. Images now persist forever!")
    print("   - Survive server restart ✅")
    print("   - Survive page refresh ✅")
    print("   - No regeneration needed ✅")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

if __name__ == "__main__":
    main()

