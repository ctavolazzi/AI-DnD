"""
Comprehensive Test Suite for Enhanced D&D Character Generator
Implements testing framework as specified in REF-400
"""

import unittest
import time
import sys
from enhanced_character_generator import (
    EnhancedCharacterGenerator, CharacterType, CharacterTone,
    EnhancedCharacter, generate_hero, generate_npc, generate_party
)

class TestCharacterGeneratorCore(unittest.TestCase):
    """REF-400.1: Test Class Structure"""

    def setUp(self):
        """Setup method for each test"""
        self.generator = EnhancedCharacterGenerator()

    def test_character_type_enum(self):
        """REF-400.2.1: Enumeration Tests - Character Types"""
        # Test that all character types exist
        expected_types = [CharacterType.HERO, CharacterType.NPC, CharacterType.VILLAIN,
                         CharacterType.MERCHANT, CharacterType.GUARD, CharacterType.NOBLE, CharacterType.SCHOLAR]

        for char_type in expected_types:
            self.assertIsInstance(char_type, CharacterType)
            self.assertIsNotNone(char_type.value)

    def test_character_tone_enum(self):
        """REF-400.2.1: Enumeration Tests - Character Tones"""
        # Test that all character tones exist
        expected_tones = [CharacterTone.REALISTIC, CharacterTone.FANTASY,
                         CharacterTone.COMEDY, CharacterTone.DRAMATIC]

        for tone in expected_tones:
            self.assertIsInstance(tone, CharacterTone)
            self.assertIsNotNone(tone.value)

    def test_generate_hero_realistic(self):
        """REF-400.2.2: Character Generation Tests - Hero Generation"""
        hero = generate_hero(3)

        # REF-400.3: Test Data Validation
        self.validate_character_data(hero)
        self.assertEqual(hero.character_type, CharacterType.HERO)
        self.assertEqual(hero.level, 3)
        self.assertIsNotNone(hero.name)
        self.assertIsNotNone(hero.race)
        self.assertIsNotNone(hero.char_class)

    def test_generate_fantasy_character(self):
        """REF-400.2.2: Character Generation Tests - Fantasy Character"""
        character = self.generator.generate_character(CharacterType.HERO, CharacterTone.FANTASY, 5)

        self.validate_character_data(character)
        self.assertEqual(character.tone, CharacterTone.FANTASY)
        self.assertEqual(character.level, 5)

    def test_generate_merchant_character(self):
        """REF-400.2.2: Character Generation Tests - Merchant Character"""
        merchant = generate_npc(CharacterType.MERCHANT)

        self.validate_character_data(merchant)
        self.assertEqual(merchant.character_type, CharacterType.MERCHANT)
        self.assertIn("Merchant's scale", merchant.equipment.type_specific_equipment)
        self.assertIn("Haggling", merchant.skills.knowledge_skills)

    def test_generate_guard_character(self):
        """REF-400.2.2: Character Generation Tests - Guard Character"""
        guard = generate_npc(CharacterType.GUARD)

        self.validate_character_data(guard)
        self.assertEqual(guard.character_type, CharacterType.GUARD)
        self.assertIn("Spear", guard.equipment.type_specific_equipment)
        self.assertIn("Vigilance", guard.skills.knowledge_skills)

    def test_generate_noble_character(self):
        """REF-400.2.2: Character Generation Tests - Noble Character"""
        noble = generate_npc(CharacterType.NOBLE)

        self.validate_character_data(noble)
        self.assertEqual(noble.character_type, CharacterType.NOBLE)
        self.assertIn("Fine clothes", noble.equipment.type_specific_equipment)
        self.assertIn("Etiquette", noble.skills.knowledge_skills)

    def test_character_serialization(self):
        """REF-400.2.3: Serialization Tests"""
        character = self.generator.generate_character()
        character_dict = self.generator.to_dict(character)

        # Test that serialization produces valid data structure
        self.assertIsInstance(character_dict, dict)
        self.assertIn("name", character_dict)
        self.assertIn("character_type", character_dict)
        self.assertIn("personality", character_dict)
        self.assertIn("background", character_dict)
        self.assertIn("stats", character_dict)
        self.assertIn("equipment", character_dict)
        self.assertIn("skills", character_dict)
        self.assertIn("spells", character_dict)

        # Test that all required fields are present
        self.assertIsNotNone(character_dict["name"])
        self.assertIsNotNone(character_dict["character_type"])
        self.assertIsNotNone(character_dict["personality"]["primary_trait"])
        self.assertIsNotNone(character_dict["background"]["occupation"])

    def test_character_summary(self):
        """REF-400.2.3: Character Summary Tests"""
        character = self.generator.generate_character()

        # Test character string representation
        char_str = str(character)
        self.assertIsInstance(char_str, str)
        self.assertIn(character.name, char_str)
        self.assertIn(str(character.level), char_str)
        self.assertIn(character.race, char_str)
        self.assertIn(character.char_class, char_str)

    def test_multiple_character_uniqueness(self):
        """REF-400.2.4: Validation Tests - Character Uniqueness"""
        characters = []
        for _ in range(10):
            char = self.generator.generate_character()
            characters.append(char)

        # Test that characters have different names (high probability)
        names = [char.name for char in characters]
        unique_names = set(names)
        self.assertGreater(len(unique_names), 1, "Characters should have different names")

        # Test that characters have different personalities
        personalities = [char.personality.primary_trait for char in characters]
        unique_personalities = set(personalities)
        self.assertGreater(len(unique_personalities), 1, "Characters should have different personalities")

    def test_character_level_scaling(self):
        """REF-400.2.4: Validation Tests - Level Scaling"""
        # Test different levels
        for level in [1, 3, 5, 10]:
            character = self.generator.generate_character(CharacterType.HERO, CharacterTone.FANTASY, level)
            self.assertEqual(character.level, level)

            # Higher level characters should have more spells
            if level > 1:
                total_spells = (len(character.spells.basic_spells) +
                               len(character.spells.combat_spells) +
                               len(character.spells.utility_spells))
                self.assertGreater(total_spells, 0, f"Level {level} character should have spells")

    def test_character_type_consistency(self):
        """REF-400.2.4: Validation Tests - Type Consistency"""
        for char_type in CharacterType:
            character = self.generator.generate_character(char_type)

            # Test that character type matches
            self.assertEqual(character.character_type, char_type)

            # Test that equipment matches character type
            expected_equipment = self.generator.equipment_by_type.get(char_type, [])
            if expected_equipment:
                for item in expected_equipment:
                    self.assertIn(item, character.equipment.type_specific_equipment)

            # Test that skills match character type
            expected_skills = self.generator.skill_data.get(char_type, [])
            if expected_skills:
                for skill in expected_skills:
                    self.assertIn(skill, character.skills.knowledge_skills)

    def validate_character_data(self, character):
        """REF-400.3: Test Data Validation"""
        # REF-400.3.1: Stat validation
        for stat in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
            value = getattr(character.stats, stat)
            self.assertGreaterEqual(value, 3, f"Stat {stat} too low: {value}")
            self.assertLessEqual(value, 20, f"Stat {stat} too high: {value}")

        # REF-400.3.2: Age validation
        age = character.appearance.get('age', 0)
        self.assertGreaterEqual(age, 18, f"Age too young: {age}")
        self.assertLessEqual(age, 80, f"Age too old: {age}")

        # REF-400.3.3: Gender validation (if applicable)
        # Note: Current implementation doesn't include gender, but structure is ready

        # REF-400.3.4: Equipment validation
        self.assertGreater(len(character.equipment.base_equipment), 0, "Character should have base equipment")

        # REF-400.3.5: Skills validation
        total_skills = (len(character.skills.combat_skills) +
                       len(character.skills.social_skills) +
                       len(character.skills.knowledge_skills) +
                       len(character.skills.utility_skills))
        self.assertGreater(total_skills, 0, "Character should have skills")

        # REF-400.3.6: Personality validation
        self.assertIsNotNone(character.personality.primary_trait)
        self.assertIsNotNone(character.personality.motivation)
        self.assertIsNotNone(character.personality.fear)

        # REF-400.3.7: Background validation
        self.assertIsNotNone(character.background.occupation)
        self.assertIsNotNone(character.background.social_class)
        self.assertGreater(len(character.background.life_events), 0, "Character should have life events")

class TestPerformanceBenchmarks(unittest.TestCase):
    """REF-400.4: Performance Tests"""

    def setUp(self):
        self.generator = EnhancedCharacterGenerator()

    def test_generation_speed(self):
        """REF-400.4.1: Generation speed test"""
        start_time = time.time()
        characters = []

        for _ in range(100):
            char = self.generator.generate_character()
            characters.append(char)

        end_time = time.time()
        generation_time = end_time - start_time
        chars_per_second = 100 / generation_time

        # REF-700.1: Benchmark Results - Generation Speed
        self.assertGreater(chars_per_second, 50, f"Generation too slow: {chars_per_second:.1f} chars/sec")
        self.assertLess(generation_time, 2.0, f"Generation took too long: {generation_time:.2f}s")

        print(f"\nPerformance Test Results:")
        print(f"  Generated: 100 characters")
        print(f"  Time: {generation_time:.2f} seconds")
        print(f"  Rate: {chars_per_second:.1f} characters/second")

    def test_memory_usage(self):
        """REF-400.4.2: Memory usage test"""
        characters = []

        # Generate 50 characters
        for _ in range(50):
            char = self.generator.generate_character()
            characters.append(char)

        # Test memory usage per character
        char_dict = self.generator.to_dict(characters[0])
        memory_per_char = sys.getsizeof(char_dict) / 1024  # KB

        # REF-700.2: Benchmark Results - Memory Usage
        self.assertLess(memory_per_char, 10, f"Memory usage too high: {memory_per_char:.1f} KB per character")

        print(f"\nMemory Test Results:")
        print(f"  Characters: 50")
        print(f"  Memory per character: {memory_per_char:.1f} KB")
        print(f"  Total memory: {memory_per_char * 50:.1f} KB")

    def test_json_serialization_speed(self):
        """REF-400.4.3: JSON serialization test"""
        characters = []

        # Generate 10 characters
        for _ in range(10):
            char = self.generator.generate_character()
            characters.append(char)

        # Test serialization speed
        start_time = time.time()
        for char in characters:
            char_dict = self.generator.to_dict(char)
        end_time = time.time()

        serialization_time = end_time - start_time
        serializations_per_second = 10 / serialization_time

        # REF-700.3: Benchmark Results - JSON Serialization
        self.assertGreater(serializations_per_second, 1000, f"Serialization too slow: {serializations_per_second:.1f} ops/sec")

        print(f"\nSerialization Test Results:")
        print(f"  Operations: 10 serializations")
        print(f"  Time: {serialization_time:.4f} seconds")
        print(f"  Rate: {serializations_per_second:.1f} operations/second")

class TestIntegrationTests(unittest.TestCase):
    """REF-400.2.6: Integration Tests"""

    def setUp(self):
        self.generator = EnhancedCharacterGenerator()

    def test_party_generation(self):
        """Test balanced party generation"""
        party = generate_party(4)

        self.assertEqual(len(party), 4)

        # Test that all party members are heroes
        for member in party:
            self.assertEqual(member.character_type, CharacterType.HERO)
            # Use the validation method from the core test class
            core_test = TestCharacterGeneratorCore()
            core_test.validate_character_data(member)

        # Test party diversity
        races = [member.race for member in party]
        classes = [member.char_class for member in party]

        # Should have some diversity (not all the same)
        self.assertGreater(len(set(races)), 1, "Party should have diverse races")
        self.assertGreater(len(set(classes)), 1, "Party should have diverse classes")

    def test_character_type_distribution(self):
        """Test character type distribution"""
        type_counts = {}

        # Generate 50 characters with random types
        for _ in range(50):
            char = self.generator.generate_character()
            char_type = char.character_type
            type_counts[char_type] = type_counts.get(char_type, 0) + 1

        # Should have reasonable distribution
        self.assertGreater(len(type_counts), 3, "Should generate multiple character types")

        # No single type should dominate (>80%)
        for char_type, count in type_counts.items():
            percentage = (count / 50) * 100
            self.assertLess(percentage, 80, f"Type {char_type} dominates: {percentage:.1f}%")

def run_performance_test():
    """REF-400.4: Performance Benchmarks"""
    print("=== Enhanced Character Generator Performance Tests ===")

    generator = EnhancedCharacterGenerator()

    # REF-400.4.1: Generation speed test
    start_time = time.time()
    characters = []
    for _ in range(100):
        char = generator.generate_character()
        characters.append(char)
    end_time = time.time()

    generation_time = end_time - start_time
    chars_per_second = 100 / generation_time

    # REF-400.4.2: Memory usage test
    memory_per_char = sys.getsizeof(generator.to_dict(characters[0])) / 1024

    # REF-400.4.3: JSON serialization test
    start_time = time.time()
    for char in characters[:10]:
        generator.to_dict(char)
    end_time = time.time()
    json_time = end_time - start_time

    print(f"\nPerformance Results:")
    print(f"  Generation Rate: {chars_per_second:.1f} characters/second")
    print(f"  Memory Usage: {memory_per_char:.1f} KB per character")
    print(f"  Serialization Rate: {10/json_time:.1f} operations/second")

    return {
        "generation_rate": chars_per_second,
        "memory_per_char": memory_per_char,
        "serialization_rate": 10/json_time
    }

if __name__ == "__main__":
    # Run the test suite
    print("=== Enhanced D&D Character Generator Test Suite ===")

    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Run performance tests
    run_performance_test()
