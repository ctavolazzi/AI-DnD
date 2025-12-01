#!/usr/bin/env python3
"""
Test script for Random User API integration with D&D Character Generator
"""

import sys
import logging

import pytest

from random_user_api import APIError, RandomUserAPI
from dnd_character_generator import DnDCharacterGenerator, create_npc, create_party, create_random_character

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
        print("\n1. Testing single user generation...")
        user = api.get_random_user()
    except APIError as exc:
        pytest.skip(f"Random User API unavailable: {exc}")
    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Unexpected error from Random User API: {exc}")

    assert user.full_name, "Random user missing full name"
    assert user.gender, "Random user missing gender"
    assert user.location_string, "Random user missing location"
    assert user.email, "Random user missing email"
    assert user.profile_picture_url, "Random user missing profile picture"
    print(f"   Name: {user.full_name}")
    print(f"   Gender: {user.gender}")
    print(f"   Location: {user.location_string}")
    print(f"   Email: {user.email}")
    print(f"   Profile Picture: {user.profile_picture_url}")

    print("\n2. Testing multiple users generation...")
    users = api.get_multiple_users(3)
    assert len(users) == 3, "Expected three users from get_multiple_users"
    print(f"   Generated {len(users)} users:")
    for i, user in enumerate(users, 1):
        print(f"   {i}. {user.full_name} ({user.gender})")

    print("\n3. Testing D&D NPC generation...")
    npc = api.get_dnd_npc("merchant")
    assert npc.title_name, "NPC missing title name"
    assert npc.location_string, "NPC missing location"
    print(f"   NPC: {npc.title_name}")
    print(f"   Location: {npc.location_string}")
    print(f"   Profile Picture: {npc.profile_picture_url}")

    print("\n4. Testing character name generation...")
    name = api.get_character_name()
    assert name, "Character name generation returned empty value"
    print(f"   Random Name: {name}")

def test_dnd_character_generator():
    """Test the D&D Character Generator"""
    print("\n" + "=" * 60)
    print("TESTING D&D CHARACTER GENERATOR")
    print("=" * 60)

    generator = DnDCharacterGenerator()

    try:
        print("\n1. Testing single character generation...")
        character = generator.generate_character()
    except APIError as exc:
        pytest.skip(f"Random User API unavailable for character generation: {exc}")
    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Error generating character: {exc}")

    assert character.bio, "Generated character missing bio"
    assert character.location, "Generated character missing location"
    assert character.ability_scores, "Generated character missing ability scores"
    print(f"   Character: {character}")
    print(f"   Bio: {character.bio}")
    print(f"   Location: {character.location}")
    print(f"   Ability Scores: {character.ability_scores}")
    print(f"   Equipment: {character.equipment[:3]}...")  # Show first 3 items

    print("\n2. Testing NPC generation...")
    npc = generator.generate_npc("merchant")
    assert npc.bio, "Generated NPC missing bio"
    assert npc.contact_info, "Generated NPC missing contact info"
    print(f"   NPC: {npc}")
    print(f"   Bio: {npc.bio}")
    print(f"   Contact Info: {npc.contact_info}")

    print("\n3. Testing party generation...")
    party = generator.generate_party(4)
    assert len(party) == 4, "Expected a party of four characters"
    print(f"   Generated party of {len(party)} characters:")
    for i, member in enumerate(party, 1):
        print(f"   {i}. {member}")

    print("\n4. Testing specific character generation...")
    fighter = generator.generate_character(char_class="Fighter", race="Human", level=3)
    assert fighter.level == 3, "Generated fighter has incorrect level"
    assert fighter.hp == fighter.max_hp, "Generated fighter HP mismatch"
    assert fighter.attack > 0, "Generated fighter missing attack"
    print(f"   Fighter: {fighter}")
    print(f"   Level: {fighter.level}")
    print(f"   HP: {fighter.hp}/{fighter.max_hp}")
    print(f"   Attack: {fighter.attack}")
    print(f"   Defense: {fighter.defense}")

def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "=" * 60)
    print("TESTING CONVENIENCE FUNCTIONS")
    print("=" * 60)

    try:
        print("\n1. Testing create_random_character()...")
        character = create_random_character(level=2)
        assert character.level == 2, "Random character has incorrect level"
        print(f"   Random Character: {character}")

        print("\n2. Testing create_npc()...")
        npc = create_npc("guard", level=1)
        assert npc.level == 1, "NPC has incorrect level"
        print(f"   Guard NPC: {npc}")

        print("\n3. Testing create_party()...")
        party = create_party(3, level=1)
        assert len(party) == 3, "Party size mismatch"
        print(f"   Party of {len(party)}:")
        for i, member in enumerate(party, 1):
            print(f"   {i}. {member}")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Error in convenience functions: {exc}")

def test_fallback_mode():
    """Test fallback mode when API is unavailable"""
    print("\n" + "=" * 60)
    print("TESTING FALLBACK MODE")
    print("=" * 60)

    generator = DnDCharacterGenerator()

    try:
        print("\n1. Testing character generation without API...")
        character = generator.generate_character(use_api=False)
        assert character.bio, "Fallback character missing bio"
        assert character.location, "Fallback character missing location"
        print(f"   Fallback Character: {character}")
        print(f"   Bio: {character.bio}")
        print(f"   Location: {character.location}")

    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Error in fallback mode: {exc}")

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
            test_func()
            results.append((test_name, True))
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
