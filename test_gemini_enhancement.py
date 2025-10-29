#!/usr/bin/env python3
"""
Test script for Gemini Enhanced Character Generation
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
from backend.app.services.gemini_character_enhancer import GeminiCharacterEnhancer
from backend.app.models.character_enhancement import EnhancementType


async def test_character_enhancement():
    """Test the character enhancement flow"""
    print("🧪 Testing Gemini Enhanced Character Generation")
    print("=" * 60)

    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY environment variable not set")
        print("   Please set your Gemini API key:")
        print("   export GEMINI_API_KEY='your-api-key-here'")
        return False

    try:
        # Initialize components
        print("🔧 Initializing components...")
        generator = CharacterGeneratorCore()
        gemini_client = GeminiClient(api_key=api_key, timeout=30)
        enhancer = GeminiCharacterEnhancer(gemini_client)

        print("✅ Components initialized successfully")

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

        # Test health check
        print("\n🏥 Testing health check...")
        health = await enhancer.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Gemini API Available: {health['gemini_api_available']}")
        print(f"   Cache Status: {health['cache_status']}")

        if not health['gemini_api_available']:
            print("❌ Gemini API not available - skipping enhancement tests")
            return False

        # Test character enhancement
        print("\n🤖 Testing character enhancement...")

        try:
            enhancement, cache_hit = await enhancer.enhance_character(
                character,
                EnhancementType.FULL
            )

            print(f"✅ Enhancement successful (cache hit: {cache_hit})")
            print(f"   Generation time: {enhancement.generation_time_ms}ms")
            print(f"   Enhancement type: {enhancement.enhancement_type}")

            # Display enhancement details
            if enhancement.backstory:
                print(f"\n📖 Backstory:")
                print(f"   {enhancement.backstory.backstory[:200]}...")

            if enhancement.personality:
                print(f"\n🧠 Personality Insights:")
                print(f"   {enhancement.personality.analysis[:200]}...")

            if enhancement.voice:
                print(f"\n🗣️ Character Voice:")
                print(f"   Speech Pattern: {enhancement.voice.speech_pattern}")
                print(f"   Sample Dialogue: {enhancement.voice.dialogue_examples[0] if enhancement.voice.dialogue_examples else 'N/A'}")

            if enhancement.quests:
                print(f"\n🎯 Quest Hooks:")
                for i, quest in enumerate(enhancement.quests.quests[:2], 1):
                    print(f"   {i}. {quest.title}")
                    print(f"      {quest.description[:100]}...")

            # Test caching
            print(f"\n💾 Testing cache...")
            enhancement2, cache_hit2 = await enhancer.enhance_character(
                character,
                EnhancementType.FULL
            )

            if cache_hit2:
                print("✅ Cache working correctly - second request served from cache")
            else:
                print("⚠️ Cache not working - second request generated new content")

            return True

        except Exception as e:
            print(f"❌ Enhancement failed: {e}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


async def test_api_endpoints():
    """Test the API endpoints (requires running server)"""
    print("\n🌐 Testing API endpoints...")

    try:
        import aiohttp

        # Test health endpoint
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("http://localhost:8000/api/character/health") as response:
                    if response.status == 200:
                        health_data = await response.json()
                        print(f"✅ Health endpoint working: {health_data['status']}")
                    else:
                        print(f"⚠️ Health endpoint returned status {response.status}")
            except aiohttp.ClientConnectorError:
                print("⚠️ API server not running - skipping endpoint tests")
                print("   Start the server with: cd backend && python -m uvicorn app.main:app --reload")
                return False

            # Test character types endpoint
            try:
                async with session.get("http://localhost:8000/api/character/types") as response:
                    if response.status == 200:
                        types_data = await response.json()
                        print(f"✅ Types endpoint working: {len(types_data['character_types'])} character types")
                    else:
                        print(f"⚠️ Types endpoint returned status {response.status}")
            except aiohttp.ClientConnectorError:
                print("⚠️ API server not running")
                return False

        return True

    except ImportError:
        print("⚠️ aiohttp not available - skipping API endpoint tests")
        return False
    except Exception as e:
        print(f"❌ API endpoint test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting Gemini Enhanced Character Generation Tests")
    print("=" * 60)

    # Test core functionality
    core_success = await test_character_enhancement()

    # Test API endpoints
    api_success = await test_api_endpoints()

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Core Enhancement: {'✅ PASS' if core_success else '❌ FAIL'}")
    print(f"API Endpoints: {'✅ PASS' if api_success else '⚠️ SKIP'}")

    if core_success:
        print("\n🎉 Gemini Enhanced Character Generation is working!")
        print("   You can now:")
        print("   - Generate characters with AI-enhanced backstories")
        print("   - Get personality insights and character voice")
        print("   - Receive personalized quest hooks")
        print("   - Use the FastAPI endpoints for integration")
    else:
        print("\n❌ Some tests failed. Check the error messages above.")

    return core_success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
