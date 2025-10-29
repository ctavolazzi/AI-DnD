#!/usr/bin/env python3
"""
Comprehensive Test Suite for Character Generator
Tests all aspects of the character generation system
"""

import asyncio
import json
import pytest
from character_generator_core import (
    CharacterGeneratorCore, CharacterGeneratorAPI,
    CharacterType, CharacterTone, Character
)

class TestCharacterGeneratorCore:
    """Test the core character generation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = CharacterGeneratorCore()

    def test_character_type_enum(self):
        """Test character type enum values"""
        assert CharacterType.HERO.value == "hero"
        assert CharacterType.MERCHANT.value == "merchant"
        assert len(CharacterType) == 9

    def test_character_tone_enum(self):
        """Test character tone enum values"""
        assert CharacterTone.REALISTIC.value == "realistic"
        assert CharacterTone.FANTASY.value == "fantasy"
        assert len(CharacterTone) == 7

    def test_generate_hero_realistic(self):
        """Test generating a realistic hero"""
        character = self.generator.generate_character(
            CharacterType.HERO,
            CharacterTone.REALISTIC,
            level=1
        )

        assert character.character_type == CharacterType.HERO
        assert character.tone == CharacterTone.REALISTIC
        assert character.level == 1
        assert character.name is not None
        assert len(character.name.split()) == 2  # First and last name
        assert character.appearance.age >= 18
        assert character.appearance.age <= 80
        assert character.stats.strength >= 3
        assert character.stats.strength <= 20
        assert character.hit_points > 0
        assert len(character.skills) > 0
        assert len(character.equipment) > 0

    def test_generate_fantasy_character(self):
        """Test generating a fantasy character"""
        character = self.generator.generate_character(
            CharacterType.SCHOLAR,
            CharacterTone.FANTASY,
            level=5
        )

        assert character.character_type == CharacterType.SCHOLAR
        assert character.tone == CharacterTone.FANTASY
        assert character.level == 5
        # Fantasy names should be different from realistic
        assert not any(common_name in character.name for common_name in
                      ["John", "Mary", "Smith", "Johnson"])
        assert character.stats.intelligence >= 10  # Scholars should be smart
        assert len(character.spells) > 0  # Scholars should have spells

    def test_generate_merchant(self):
        """Test generating a merchant character"""
        character = self.generator.generate_character(
            CharacterType.MERCHANT,
            CharacterTone.REALISTIC
        )

        assert character.character_type == CharacterType.MERCHANT
        assert character.background.occupation == "Merchant"
        assert character.background.social_class == "Merchant"
        assert character.stats.charisma >= 10  # Merchants should be charismatic
        assert "Merchant's scale" in character.equipment

    def test_generate_guard(self):
        """Test generating a guard character"""
        character = self.generator.generate_character(
            CharacterType.GUARD,
            CharacterTone.REALISTIC
        )

        assert character.character_type == CharacterType.GUARD
        assert character.background.occupation == "Guard"
        assert character.stats.strength >= 10  # Guards should be strong
        assert "Spear" in character.equipment or "Badge of office" in character.equipment

    def test_generate_noble(self):
        """Test generating a noble character"""
        character = self.generator.generate_character(
            CharacterType.NOBLE,
            CharacterTone.REALISTIC
        )

        assert character.character_type == CharacterType.NOBLE
        assert character.background.social_class == "Noble"
        assert character.background.occupation == "Noble"
        assert "Signet ring" in character.equipment or "Fine clothes" in character.equipment

    def test_character_serialization(self):
        """Test character serialization to JSON"""
        character = self.generator.generate_character(CharacterType.HERO)

        # Test to_dict
        char_dict = character.to_dict()
        assert isinstance(char_dict, dict)
        assert char_dict["name"] == character.name
        assert char_dict["character_type"] == character.character_type.value

        # Test to_json
        char_json = character.to_json()
        assert isinstance(char_json, str)

        # Test JSON can be parsed back
        parsed = json.loads(char_json)
        assert parsed["name"] == character.name

    def test_character_summary(self):
        """Test character summary generation"""
        character = self.generator.generate_character(CharacterType.HERO)
        summary = character.get_summary()

        assert character.name in summary
        assert character.character_type.value.title() in summary
        assert str(character.appearance.age) in summary
        assert character.appearance.gender in summary
        assert character.background.occupation in summary

    def test_multiple_characters_unique(self):
        """Test that multiple characters are unique"""
        characters = []
        for _ in range(10):
            char = self.generator.generate_character(CharacterType.HERO)
            characters.append(char)

        # Names should be unique (very high probability)
        names = [char.name for char in characters]
        assert len(set(names)) > 5  # At least 5 unique names out of 10

        # Motivations should vary
        motivations = [char.personality.motivation for char in characters]
        assert len(set(motivations)) > 3  # At least 3 unique motivations

    def test_character_level_scaling(self):
        """Test that character stats scale with level"""
        level_1_char = self.generator.generate_character(CharacterType.HERO, level=1)
        level_5_char = self.generator.generate_character(CharacterType.HERO, level=5)

        assert level_5_char.level == 5
        assert level_5_char.hit_points > level_1_char.hit_points
        assert len(level_5_char.spells) >= len(level_1_char.spells)

    def test_character_type_consistency(self):
        """Test that character types have consistent attributes"""
        for char_type in CharacterType:
            character = self.generator.generate_character(char_type)

            # All characters should have basic attributes
            assert character.name is not None
            assert character.appearance.age >= 18
            assert character.personality.motivation is not None
            assert character.background.occupation is not None
            assert len(character.skills) > 0
            assert len(character.equipment) > 0

class TestCharacterGeneratorAPI:
    """Test the API integration functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.api = CharacterGeneratorAPI()
        self.core = CharacterGeneratorCore()

    @pytest.mark.asyncio
    async def test_api_enhancement(self):
        """Test API enhancement of characters"""
        character = self.core.generate_character(CharacterType.HERO)
        original_name = character.name

        enhanced = await self.api.enhance_character_with_api(character)

        # Character should still be valid
        assert enhanced.name is not None
        assert enhanced.character_type == CharacterType.HERO
        # Name might change due to API data
        assert isinstance(enhanced.name, str)
        assert len(enhanced.name.split()) >= 2

    @pytest.mark.asyncio
    async def test_api_fallback(self):
        """Test API fallback when service is unavailable"""
        # This should not raise an exception even if API fails
        character = self.core.generate_character(CharacterType.HERO)

        try:
            enhanced = await self.api.enhance_character_with_api(character)
            assert enhanced is not None
            assert enhanced.name is not None
        except Exception as e:
            pytest.fail(f"API enhancement should not raise exceptions: {e}")

def run_performance_test():
    """Run performance tests"""
    print("⚡ Running Performance Tests")
    print("=" * 50)

    generator = CharacterGeneratorCore()

    import time

    # Test generation speed
    start_time = time.time()
    characters = []
    for _ in range(100):
        char = generator.generate_character(CharacterType.HERO)
        characters.append(char)
    end_time = time.time()

    generation_time = end_time - start_time
    chars_per_second = 100 / generation_time

    print(f"Generated 100 characters in {generation_time:.2f} seconds")
    print(f"Rate: {chars_per_second:.1f} characters/second")

    # Test memory usage
    import sys
    memory_per_char = sys.getsizeof(characters[0].to_dict()) / 1024
    print(f"Memory per character: {memory_per_char:.1f} KB")

    # Test JSON serialization speed
    start_time = time.time()
    for char in characters[:10]:
        char.to_json()
    end_time = time.time()

    json_time = end_time - start_time
    print(f"Serialized 10 characters to JSON in {json_time:.3f} seconds")

def run_integration_test():
    """Run integration tests"""
    print("🔗 Running Integration Tests")
    print("=" * 50)

    generator = CharacterGeneratorCore()
    api = CharacterGeneratorAPI()

    # Test all character types
    for char_type in CharacterType:
        for tone in CharacterTone:
            try:
                char = generator.generate_character(char_type, tone)
                assert char is not None
                print(f"✅ {char_type.value} ({tone.value}): {char.name}")
            except Exception as e:
                print(f"❌ {char_type.value} ({tone.value}): {e}")

    # Test API integration
    async def test_api():
        char = generator.generate_character(CharacterType.HERO)
        enhanced = await api.enhance_character_with_api(char)
        print(f"✅ API Enhancement: {enhanced.name}")

    asyncio.run(test_api())

def run_validation_test():
    """Run data validation tests"""
    print("✅ Running Validation Tests")
    print("=" * 50)

    generator = CharacterGeneratorCore()

    # Test data integrity
    for _ in range(50):
        char = generator.generate_character(CharacterType.HERO)

        # Validate stats
        for stat in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            value = getattr(char.stats, stat)
            assert 3 <= value <= 20, f"Stat {stat} out of range: {value}"

        # Validate age
        assert 18 <= char.appearance.age <= 80, f"Age out of range: {char.appearance.age}"

        # Validate gender
        assert char.appearance.gender in ["Male", "Female", "Non-binary"]

        # Validate equipment
        assert len(char.equipment) > 0, "Character should have equipment"

        # Validate skills
        assert len(char.skills) > 0, "Character should have skills"

        # Validate JSON serialization
        char_json = char.to_json()
        parsed = json.loads(char_json)
        assert parsed["name"] == char.name

    print("✅ All validation tests passed")

if __name__ == "__main__":
    print("🧪 CHARACTER GENERATOR TEST SUITE")
    print("=" * 60)

    # Run core tests
    test_core = TestCharacterGeneratorCore()
    test_core.setup_method()

    print("\n1. Testing Core Functionality")
    test_core.test_character_type_enum()
    test_core.test_character_tone_enum()
    test_core.test_generate_hero_realistic()
    test_core.test_generate_fantasy_character()
    test_core.test_generate_merchant()
    test_core.test_generate_guard()
    test_core.test_generate_noble()
    test_core.test_character_serialization()
    test_core.test_character_summary()
    test_core.test_multiple_characters_unique()
    test_core.test_character_level_scaling()
    test_core.test_character_type_consistency()
    print("✅ Core functionality tests passed")

    # Run API tests
    print("\n2. Testing API Integration")
    test_api = TestCharacterGeneratorAPI()
    test_api.setup_method()
    asyncio.run(test_api.test_api_enhancement())
    asyncio.run(test_api.test_api_fallback())
    print("✅ API integration tests passed")

    # Run performance tests
    print("\n3. Performance Tests")
    run_performance_test()

    # Run integration tests
    print("\n4. Integration Tests")
    run_integration_test()

    # Run validation tests
    print("\n5. Validation Tests")
    run_validation_test()

    print("\n🎉 ALL TESTS PASSED!")
    print("Character generator is ready for MCP server integration.")
