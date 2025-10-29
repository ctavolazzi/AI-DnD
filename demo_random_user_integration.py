#!/usr/bin/env python3
"""
Demonstration script showing Random User API integration with D&D Character Generation
"""

from dnd_character_generator import create_random_character, create_npc, create_party
from random_user_api import get_random_name, get_multiple_npcs

def demo_character_generation():
    """Demonstrate the enhanced character generation capabilities"""

    print("🎲 D&D CHARACTER GENERATION WITH RANDOM USER API")
    print("=" * 60)

    # 1. Generate a random character
    print("\n1. 🧙‍♂️ RANDOM CHARACTER GENERATION")
    print("-" * 40)
    character = create_random_character(level=3)
    print(f"Character: {character}")
    print(f"Bio: {character.bio}")
    print(f"Location: {character.location}")
    print(f"Profile Picture: {character.profile_picture_url}")
    print(f"Contact: {character.contact_info.get('email', 'N/A')}")
    print(f"Stats: HP {character.hp}/{character.max_hp}, Attack {character.attack}, Defense {character.defense}")

    # 2. Generate specific NPCs
    print("\n2. 🏪 NPC GENERATION")
    print("-" * 40)
    npc_types = ["merchant", "guard", "noble", "priest"]
    for npc_type in npc_types:
        npc = create_npc(npc_type, level=2)
        print(f"{npc_type.title()}: {npc.name} - {npc.char_class}")
        print(f"  Bio: {npc.bio}")
        print(f"  Contact: {npc.contact_info.get('email', 'N/A')}")
        print()

    # 3. Generate a balanced party
    print("\n3. 👥 BALANCED PARTY GENERATION")
    print("-" * 40)
    party = create_party(4, level=2)
    print("Adventuring Party:")
    for i, member in enumerate(party, 1):
        print(f"{i}. {member.name} - Level {member.level} {member.race} {member.char_class}")
        print(f"   From: {member.location}")
        print(f"   Bio: {member.bio[:80]}...")
        print()

    # 4. Generate just names for quick use
    print("\n4. 📝 QUICK NAME GENERATION")
    print("-" * 40)
    print("Random Names:")
    for i in range(5):
        name = get_random_name()
        print(f"  {i+1}. {name}")

    # 5. Generate multiple NPCs for a tavern
    print("\n5. 🍺 TAVERN NPCs")
    print("-" * 40)
    tavern_npcs = get_multiple_npcs(3)
    print("Tavern Patrons:")
    for i, npc in enumerate(tavern_npcs, 1):
        print(f"{i}. {npc.full_name} ({npc.gender})")
        print(f"   From: {npc.location_string}")
        print(f"   Picture: {npc.profile_picture_url}")
        print()

def demo_api_features():
    """Demonstrate specific API features"""

    print("\n🔧 API FEATURES DEMONSTRATION")
    print("=" * 60)

    from random_user_api import RandomUserAPI
    api = RandomUserAPI()

    # 1. Different nationalities
    print("\n1. 🌍 NATIONALITY DIVERSITY")
    print("-" * 40)
    nationalities = ["US", "GB", "FR", "DE", "ES"]
    for nat in nationalities:
        try:
            user = api.get_random_user(nationality=nat)
            print(f"{nat}: {user.full_name} from {user.location_string}")
        except Exception as e:
            print(f"{nat}: Error - {e}")

    # 2. Gender-specific generation
    print("\n2. 👨👩 GENDER-SPECIFIC GENERATION")
    print("-" * 40)
    for gender in ["male", "female"]:
        try:
            user = api.get_random_user(gender=gender)
            print(f"{gender.title()}: {user.full_name} ({user.gender})")
        except Exception as e:
            print(f"{gender.title()}: Error - {e}")

    # 3. Seeded generation (reproducible)
    print("\n3. 🎲 SEEDED GENERATION (Reproducible)")
    print("-" * 40)
    seed = "dnd-adventure"
    try:
        user1 = api.get_random_user(seed=seed)
        user2 = api.get_random_user(seed=seed)
        print(f"Seed '{seed}':")
        print(f"  First call: {user1.full_name}")
        print(f"  Second call: {user2.full_name}")
        print(f"  Same result: {user1.full_name == user2.full_name}")
    except Exception as e:
        print(f"Seeded generation error: {e}")

def demo_fallback_mode():
    """Demonstrate fallback mode when API is unavailable"""

    print("\n🛡️ FALLBACK MODE DEMONSTRATION")
    print("=" * 60)

    from dnd_character_generator import DnDCharacterGenerator
    generator = DnDCharacterGenerator()

    print("\nCharacter generation without API (fallback mode):")
    character = generator.generate_character(use_api=False)
    print(f"Fallback Character: {character}")
    print(f"Bio: {character.bio}")
    print(f"Location: {character.location}")
    print(f"Profile Picture: {character.profile_picture_url or 'N/A'}")

if __name__ == "__main__":
    try:
        demo_character_generation()
        demo_api_features()
        demo_fallback_mode()

        print("\n🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("The Random User API integration successfully enhances D&D character generation")
        print("with realistic names, backgrounds, locations, and profile pictures.")
        print("\nKey Benefits:")
        print("✅ Realistic character names and backgrounds")
        print("✅ Visual character representation with profile pictures")
        print("✅ Contact information for roleplay scenarios")
        print("✅ Cultural diversity through nationality selection")
        print("✅ Reliable fallback ensures consistent functionality")

    except Exception as e:
        print(f"\n❌ Demonstration error: {e}")
        print("This might be due to network issues or API unavailability.")
        print("The fallback mode should still work for basic character generation.")
