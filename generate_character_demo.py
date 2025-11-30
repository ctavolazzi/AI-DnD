#!/usr/bin/env python3
"""Generate a complete D&D character using Gemini AI."""

import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

# Load API key
load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("🎲 AI-DnD Character Generator")
print("="*70 + "\n")

# Create the model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Generate a character
prompt = """Create a detailed D&D 5e character. Include:
1. Name and race
2. Class and level
3. Background story (2-3 paragraphs)
4. Personality traits
5. Key stats (STR, DEX, CON, INT, WIS, CHA)
6. Special abilities or signature moves
7. A dramatic scene from their past

Make it epic and cinematic!"""

print("🤖 Generating character with Gemini AI...")
print("   This may take a moment...\n")

try:
    response = model.generate_content(prompt)
    character_text = response.text

    print("✅ Character Generated!\n")
    print("="*70)
    print(character_text)
    print("="*70)

    # Save to file
    with open('generated_character.txt', 'w') as f:
        f.write(character_text)
    print("\n💾 Character saved to: generated_character.txt")

    # Now generate a quest for this character
    print("\n" + "="*70)
    print("\n🗺️  Generating a quest for this character...\n")

    quest_prompt = f"""Based on this D&D character:

{character_text}

Create an exciting quest hook (2-3 paragraphs) that:
1. Fits their background and motivations
2. Has high stakes
3. Includes a specific location to explore
4. Has a mysterious antagonist or threat

Make it dramatic and urgent!"""

    quest_response = model.generate_content(quest_prompt)
    quest_text = quest_response.text

    print("✅ Quest Generated!\n")
    print("="*70)
    print(quest_text)
    print("="*70)

    # Save quest
    with open('generated_quest.txt', 'w') as f:
        f.write(f"CHARACTER:\n{character_text}\n\n")
        f.write(f"QUEST:\n{quest_text}")
    print("\n💾 Full adventure saved to: generated_quest.txt")

    # Generate a dramatic opening scene
    print("\n" + "="*70)
    print("\n🎭 Generating opening scene...\n")

    scene_prompt = f"""Write a dramatic opening scene (200-300 words) for this quest:

CHARACTER: {character_text[:500]}...

QUEST: {quest_text[:500]}...

Write it in second person ("You..."), present tense, with vivid sensory details. Make it atmospheric and exciting!"""

    scene_response = model.generate_content(scene_prompt)
    scene_text = scene_response.text

    print("✅ Opening Scene Generated!\n")
    print("="*70)
    print(scene_text)
    print("="*70)

    # Save complete adventure
    complete_adventure = {
        "character": character_text,
        "quest": quest_text,
        "opening_scene": scene_text
    }

    with open('complete_adventure.json', 'w') as f:
        json.dump(complete_adventure, f, indent=2)

    print("\n💾 Complete adventure package saved to: complete_adventure.json")
    print("\n" + "="*70)
    print("🎉 ADVENTURE READY!")
    print("="*70)
    print("\nGenerated files:")
    print("  • generated_character.txt - Your character")
    print("  • generated_quest.txt - Character + Quest")
    print("  • complete_adventure.json - Full package")
    print("\nYou can now:")
    print("  1. Use this in the Interactive Story Theater")
    print("  2. Continue the adventure manually")
    print("  3. Generate pixel art sprites for your character")
    print("="*70)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
