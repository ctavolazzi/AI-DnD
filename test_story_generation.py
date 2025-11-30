#!/usr/bin/env python3
"""Quick test to generate an illustrated adventure chapter."""

import requests
import json
import uuid

BASE_URL = "http://localhost:5002"

print("🎲 Starting Interactive Story Theater Demo...")
print("="*60 + "\n")

# Step 1: Start a new adventure
print("1️⃣ Starting new adventure session...")
session_id = str(uuid.uuid4())[:8]

start_data = {
    "session_id": session_id,
    "theme": "A dwarven warrior's quest to reclaim his ancestral mountain fortress",
    "model": "gemini"
}

try:
    response = requests.post(f"{BASE_URL}/start-adventure", json=start_data, timeout=60)

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Adventure started! Session ID: {result.get('session_id', session_id)}")

        if 'characters' in result:
            print(f"\n👥 CHARACTERS ({len(result['characters'])}):")
            for char in result['characters']:
                print(f"  • {char['name']} - {char['class']} (HP: {char['hp']}/{char['max_hp']})")

        if 'quest' in result:
            print(f"\n🎯 QUEST:")
            print(f"  {result['quest']}")

        if 'first_scene' in result:
            print(f"\n📖 OPENING SCENE:")
            print(f"  {result['first_scene'].get('narrative', 'No narrative available')[:200]}...")

        print("\n" + "="*60 + "\n")

        # Save session info
        with open('adventure_session.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("💾 Session info saved to adventure_session.json\n")

        # Step 2: Generate next scene with player action
        print("2️⃣ Generating next scene with player action...")

        next_scene_data = {
            "session_id": session_id,
            "player_action": "I approach the ancient gates cautiously, my hand on my axe as thunder rumbles overhead"
        }

        response2 = requests.post(f"{BASE_URL}/next-scene", json=next_scene_data, timeout=120)

        if response2.status_code == 200:
            scene_result = response2.json()
            print("✅ Scene generated!\n")

            if 'scene' in scene_result:
                scene = scene_result['scene']
                print("📖 NARRATIVE:")
                print(f"  {scene.get('narrative', 'No narrative')}\n")

                if scene.get('image_generated'):
                    print("🖼️  Image generated for this scene!")

            # Save scene
            with open('latest_scene.json', 'w') as f:
                json.dump(scene_result, f, indent=2)
            print("\n💾 Scene saved to latest_scene.json")

        else:
            print(f"❌ Scene generation failed: HTTP {response2.status_code}")
            print(response2.text)

    else:
        print(f"❌ Failed to start adventure: HTTP {response.status_code}")
        print(response.text)

except requests.exceptions.Timeout:
    print("⏱️  Request timed out - AI generation takes time!")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("🎭 Demo complete! Check the JSON files for full results.")
print("="*60)
