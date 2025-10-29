#!/usr/bin/env python3
"""
Test script for Random User API integration with D&D Character Generator
"""

import sys
import logging
from random_user_api import RandomUserAPI, APIError
from dnd_character_generator import DnDCharacterGenerator, create_random_character, create_npc, create_party

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_random_user_api():
    """Test the Random User API directly"""
    print("=" * 60)
    print("TESTING RANDOM USER API")
    print("=" * 60)

    api = RandomUserAPI()

    try:
        # Test single user
        print("\n1. Testing single user generation...")
        user = api.get_random_user()
        print(f"   Name: {user.full_name}")
        print(f"   Gender: {user.gender}")
        print(f"   Location: {user.location_string}")
        print(f"   Email: {user.email}")
        print(f"   Profile Picture: {user.profile_picture_url}")

        # Test multiple users
        print("\n2. Testing multiple users generation...")
        users = api.get_multiple_users(3)
        print(f"   Generated {len(users)} users:")
        for i, user in enumerate(users, 1):
            print(f"   {i}. {user.full_name} ({user.gender})")

        # Test D&D NPC
        print("\n3. Testing D&D NPC generation...")
        npc = api.get_dnd_npc("merchant")
        print(f"   NPC: {npc.title_name}")
        print(f"   Location: {npc.location_string}")
        print(f"   Profile Picture: {npc.profile_picture_url}")

        # Test character name only
        print("\n4. Testing character name generation...")
        name = api.get_character_name()
        print(f"   Random Name: {name}")

        print("\n✅ Random User API tests passed!")
        return True

    except APIError as e:
        print(f"\n❌ API Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def test_dnd_character_generator():
    """Test the D&D Character Generator"""
    print("\n" + "=" * 60)
    print("TESTING D&D CHARACTER GENERATOR")
    print("=" * 60)

    generator = DnDCharacterGenerator()

    try:
        # Test single character
        print("\n1. Testing single character generation...")
        character = generator.generate_character()
        print(f"   Character: {character}")
        print(f"   Bio: {character.bio}")
        print(f"   Location: {character.location}")
        print(f"   Ability Scores: {character.ability_scores}")
        print(f"   Equipment: {character.equipment[:3]}...")  # Show first 3 items

        # Test NPC
        print("\n2. Testing NPC generation...")
        npc = generator.generate_npc("merchant")
        print(f"   NPC: {npc}")
        print(f"   Bio: {npc.bio}")
        print(f"   Contact Info: {npc.contact_info}")

        # Test party
        print("\n3. Testing party generation...")
        party = generator.generate_party(4)
        print(f"   Generated party of {len(party)} characters:")
        for i, member in enumerate(party, 1):
            print(f"   {i}. {member}")

        # Test specific character
        print("\n4. Testing specific character generation...")
        fighter = generator.generate_character(char_class="Fighter", race="Human", level=3)
        print(f"   Fighter: {fighter}")
        print(f"   Level: {fighter.level}")
        print(f"   HP: {fighter.hp}/{fighter.max_hp}")
        print(f"   Attack: {fighter.attack}")
        print(f"   Defense: {fighter.defense}")

        print("\n✅ D&D Character Generator tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error in D&D Character Generator: {e}")
        return False

def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTIONS")
    print("=" * 60)

    try:
        # Test create_random_character
        print("\n1. Testing create_random_character()...")
        character = create_random_character(level=2)
        print(f"   Random Character: {character}")

        # Test create_npc
        print("\n2. Testing create_npc()...")
        npc = create_npc("guard", level=1)
        print(f"   Guard NPC: {npc}")

        # Test create_party
        print("\n3. Testing create_party()...")
        party = create_party(3, level=1)
        print(f"   Party of {len(party)}:")
        for i, member in enumerate(party, 1):
            print(f"   {i}. {member}")

        print("\n✅ Convenience functions tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error in convenience functions: {e}")
        return False

def test_fallback_mode():
    """Test fallback mode when API is unavailable"""
    print("\n" + "=" * 60)
    print("TESTING FALLBACK MODE")
    print("=" * 60)

    generator = DnDCharacterGenerator()

    try:
        # Test with API disabled
        print("\n1. Testing character generation without API...")
        character = generator.generate_character(use_api=False)
        print(f"   Fallback Character: {character}")
        print(f"   Bio: {character.bio}")
        print(f"   Location: {character.location}")

        print("\n✅ Fallback mode tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Error in fallback mode: {e}")
        return False

def main():
    """Run all tests"""
    print("RANDOM USER API INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Random User API", test_random_user_api),
        ("D&D Character Generator", test_dnd_character_generator),
        ("Convenience Functions", test_convenience_functions),
        ("Fallback Mode", test_fallback_mode)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Random User API integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
