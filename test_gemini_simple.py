#!/usr/bin/env python3
"""
Simple test script for Gemini Enhanced Character Generation
"""
import os
import sys
import asyncio
import json
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from character_generator_core import CharacterGeneratorCore, CharacterType, CharacterTone
from backend.app.services.gemini_client import GeminiClient


async def test_gemini_text_generation():
    """Test basic Gemini text generation"""
    print("🧪 Testing Gemini Text Generation")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Please set your Gemini API key:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        return False

    try:
        # Initialize Gemini client
        print("🔧 Initializing Gemini client...")
        gemini_client = GeminiClient(api_key=api_key, timeout=30)

        print("✅ Gemini client initialized successfully")

        # Test basic text generation
        print("\n📝 Testing basic text generation...")
        test_prompt = "Write a brief D&D character backstory for a brave warrior named Aldric."

        try:
            response, generation_time = gemini_client.generate_text(test_prompt)

            print(f"✅ Text generation successful!")
            print(f"   Generation time: {generation_time}ms")
            print(f"   Response length: {len(response)} characters")
            print(f"\n📖 Sample response:")
            print(f"   {response[:300]}...")

            return True

        except Exception as e:
            print(f"❌ Text generation failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_character_generation():
    """Test character generation without enhancement"""
    print("\n🧪 Testing Character Generation")
    print("=" * 50)

    try:
        # Initialize character generator
        print("🔧 Initializing character generator...")
        generator = CharacterGeneratorCore()

        print("✅ Character generator initialized successfully")

        # Generate base character
        print("\n📝 Generating base character...")
        character = generator.generate_character(
            character_type=CharacterType.HERO,
            tone=CharacterTone.FANTASY,
            level=3
        )

        print(f"✅ Generated character: {character.name}")
        print(f"   Type: {character.character_type.value}")
        print(f"   Level: {character.level}")
        print(f"   Motivation: {character.personality.motivation}")
        print(f"   Secret: {character.personality.secret}")
        print(f"   Goals: {character.background.goals}")

        # Convert to dict for API testing
        character_dict = character.to_dict()
        print(f"\n📊 Character data structure:")
        print(f"   Keys: {list(character_dict.keys())}")
        print(f"   Stats: STR{character.stats.strength} DEX{character.stats.dexterity} INT{character.stats.intelligence}")

        return True

    except Exception as e:
        print(f"❌ Character generation failed: {e}")
        return False


async def test_enhancement_prompts():
    """Test enhancement prompt generation"""
    print("\n🧪 Testing Enhancement Prompts")
    print("=" * 50)

    try:
        # Initialize Gemini client
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not set - skipping enhancement test")
            return False

        gemini_client = GeminiClient(api_key=api_key, timeout=30)

        # Generate character for testing
        generator = CharacterGeneratorCore()
        character = generator.generate_character(
            character_type=CharacterType.HERO,
            tone=CharacterTone.FANTASY,
            level=3
        )

        # Extract character data
        character_data = {
            "name": character.name,
            "character_type": character.character_type.value,
            "age": character.appearance.age,
            "gender": character.appearance.gender,
            "occupation": character.background.occupation,
            "primary_trait": character.personality.primary_trait,
            "secondary_trait": character.personality.secondary_trait,
            "motivation": character.personality.motivation,
            "fear": character.personality.fear,
            "secret": character.personality.secret,
            "quirk": character.personality.quirk,
            "goals": character.background.goals,
            "tone": character.tone.value
        }

        print(f"📝 Testing enhancement prompts for: {character.name}")

        # Test backstory prompt
        print("\n📖 Testing backstory generation...")
        try:
            enhancement_data, generation_time = gemini_client.generate_character_enhancement(
                character_data,
                "backstory"
            )

            print(f"✅ Backstory generation successful!")
            print(f"   Generation time: {generation_time}ms")
            print(f"   Response length: {len(enhancement_data.get('raw_response', ''))} characters")

            # Show sample
            backstory = enhancement_data.get('raw_response', '')
            if backstory:
                print(f"\n📖 Sample backstory:")
                print(f"   {backstory[:300]}...")

        except Exception as e:
            print(f"❌ Backstory generation failed: {e}")
            return False

        return True

    except Exception as e:
        print(f"❌ Enhancement prompt test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Gemini Enhanced Character Generation Tests")
    print("=" * 60)

    # Test basic text generation
    text_success = await test_gemini_text_generation()

    # Test character generation
    char_success = await test_character_generation()

    # Test enhancement prompts
    enhancement_success = await test_enhancement_prompts()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Gemini Text Generation: {'✅ PASS' if text_success else '❌ FAIL'}")
    print(f"Character Generation: {'✅ PASS' if char_success else '❌ FAIL'}")
    print(f"Enhancement Prompts: {'✅ PASS' if enhancement_success else '❌ FAIL'}")

    overall_success = text_success and char_success and enhancement_success

    if overall_success:
        print("\n🎉 Gemini Enhanced Character Generation is working!")
        print("   Core functionality verified:")
        print("   - ✅ Gemini text generation")
        print("   - ✅ Character generation")
        print("   - ✅ Enhancement prompts")
        print("\n   Next steps:")
        print("   - Start the FastAPI server: cd backend && python -m uvicorn app.main:app --reload")
        print("   - Test API endpoints at http://localhost:8000/docs")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

    return overall_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
