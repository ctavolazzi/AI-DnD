"""
Combat System Tests

Tests for the core RPG systems: stats, characters, and combat math.
Run with: pytest pygame_mvp/tests/test_combat.py -v
Or standalone: python pygame_mvp/tests/test_combat.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pygame_mvp.game.systems import (
    Character, Player, CombatSystem, Stats,
    CharacterClass, Item, ItemType, create_enemy
)


# =============================================================================
# STATS TESTS
# =============================================================================

class TestStats:
    """Test the Stats dataclass and its operations."""

    def test_default_stats(self):
        """Verify default stat values (average human = 10)."""
        stats = Stats()
        assert stats.strength == 10
        assert stats.dexterity == 10
        assert stats.intelligence == 10
        assert stats.constitution == 10

    def test_zero_stats(self):
        """Verify Stats.zero() creates all-zero stats."""
        stats = Stats.zero()
        assert stats.strength == 0
        assert stats.dexterity == 0
        assert stats.intelligence == 0
        assert stats.constitution == 0

    def test_bonus_stats(self):
        """Verify Stats.bonus() creates stats with specified bonuses."""
        stats = Stats.bonus(strength=5)
        assert stats.strength == 5
        assert stats.dexterity == 0
        assert stats.intelligence == 0
        assert stats.constitution == 0

    def test_custom_stats(self):
        """Verify custom stat initialization."""
        stats = Stats(strength=15, dexterity=12, intelligence=8, constitution=14)
        assert stats.strength == 15
        assert stats.dexterity == 12
        assert stats.intelligence == 8
        assert stats.constitution == 14

    def test_stats_addition(self):
        """Verify stats add up correctly (Base + Gear bonuses)."""
        base = Stats(strength=10, dexterity=5, intelligence=10, constitution=10)
        bonus = Stats(strength=5, dexterity=5, intelligence=0, constitution=2)
        total = base + bonus

        assert total.strength == 15
        assert total.dexterity == 10
        assert total.intelligence == 10  # 10 + 0
        assert total.constitution == 12  # 10 + 2

    def test_average_factory(self):
        """Verify the average factory returns baseline 10s."""
        avg = Stats.average()
        assert (avg.strength, avg.dexterity, avg.intelligence, avg.constitution) == (10, 10, 10, 10)


# =============================================================================
# CHARACTER TESTS
# =============================================================================

class TestCharacter:
    """Test the base Character class."""

    def test_character_creation(self):
        """Verify basic character initialization."""
        char = Character("TestHero")
        assert char.name == "TestHero"
        assert char.level == 1
        assert char.current_hp == 20
        assert char.max_hp == 20

    def test_character_equipment_slots(self):
        """Verify equipment slots exist."""
        char = Character("Test")
        assert "weapon" in char.equipment
        assert "armor" in char.equipment
        assert char.equipment["weapon"] is None
        assert char.equipment["armor"] is None

    def test_equip_weapon(self):
        """Verify equipping a weapon works."""
        char = Character("Fighter")
        sword = Item(
            name="Iron Sword",
            item_type=ItemType.WEAPON,
            value=50,
            damage_min=5,
            damage_max=10
        )
        char.equip(sword)
        assert char.equipment["weapon"] == sword
        assert char.equipment["weapon"].name == "Iron Sword"

    def test_total_stats_with_equipment(self):
        """Verify total_stats includes equipment bonuses."""
        char = Character("Test")
        char.base_stats = Stats(strength=10, dexterity=10, intelligence=10, constitution=10)

        # Use Stats.bonus() for equipment bonuses (defaults to 0)
        magic_sword = Item(
            name="Sword of Might",
            item_type=ItemType.WEAPON,
            value=200,
            damage_min=8,
            damage_max=12,
            stats_bonus=Stats.bonus(strength=5)
        )
        char.equip(magic_sword)

        assert char.total_stats.strength == 15  # 10 base + 5 from sword
        assert char.total_stats.dexterity == 10  # 10 base + 0 from sword


# =============================================================================
# HP CLAMPING TESTS
# =============================================================================

class TestHPClamping:
    """Test HP clamping behavior."""

    def test_hp_cannot_exceed_max(self):
        """Verify HP cannot exceed max."""
        char = Character("Test", max_hp=20)
        char.current_hp = 100  # Should clamp to 20
        assert char.current_hp == 20

    def test_hp_cannot_go_negative(self):
        """Verify HP cannot go below zero."""
        char = Character("Test")
        char.current_hp = -50  # Should clamp to 0
        assert char.current_hp == 0

    def test_healing_respects_max(self):
        """Verify healing doesn't exceed max HP."""
        char = Character("Test", max_hp=20)
        char.current_hp = 15
        char.current_hp += 10  # Should only go to 20
        assert char.current_hp == 20

    def test_max_hp_change_clamps_current(self):
        """Verify changing max_hp clamps current_hp."""
        char = Character("Test", max_hp=50)
        char.current_hp = 50
        char.max_hp = 30  # Current HP should clamp to 30
        assert char.current_hp == 30


# =============================================================================
# PLAYER TESTS
# =============================================================================

class TestPlayer:
    """Test the Player class with class-specific stats."""

    def test_fighter_stats(self):
        """Verify Fighter class gets correct baseline stats."""
        fighter = Player("Conan", CharacterClass.FIGHTER)
        assert fighter.base_stats.strength == 14
        assert fighter.base_stats.dexterity == 10
        assert fighter.max_hp == 30

    def test_wizard_stats(self):
        """Verify Wizard class gets correct baseline stats."""
        wizard = Player("Gandalf", CharacterClass.WIZARD)
        assert wizard.base_stats.intelligence == 16
        assert wizard.base_stats.strength == 6
        assert wizard.max_hp == 18

    def test_rogue_stats(self):
        """Verify Rogue class gets correct baseline stats."""
        rogue = Player("Shadow", CharacterClass.ROGUE)
        assert rogue.base_stats.dexterity == 14
        assert rogue.max_hp == 24

    def test_cleric_stats(self):
        """Verify Cleric class gets correct baseline stats."""
        cleric = Player("Healer", CharacterClass.CLERIC)
        assert cleric.base_stats.intelligence == 14
        assert cleric.max_hp == 26

    def test_player_starts_at_full_hp(self):
        """Verify player starts at max HP."""
        player = Player("Test", CharacterClass.FIGHTER)
        assert player.current_hp == player.max_hp


# =============================================================================
# COMBAT TESTS
# =============================================================================

class TestCombatSystem:
    """Test the CombatSystem attack resolution."""

    def test_attack_returns_dict(self):
        """Verify attack returns expected structure."""
        attacker = Character("Attacker")
        defender = Character("Defender")

        result = CombatSystem.calculate_attack(attacker, defender)

        assert "damage" in result
        assert "hit" in result
        assert "crit" in result
        assert "msg" in result

    def test_attack_with_weapon(self):
        """Verify weapon damage is used in attack."""
        attacker = Character("Attacker")
        attacker.base_stats = Stats(strength=15, dexterity=50)

        sword = Item("Test Sword", ItemType.WEAPON, value=10, damage_min=5, damage_max=10)
        attacker.equip(sword)

        defender = Character("Defender")
        defender.base_stats = Stats(dexterity=5)

        hits = 0
        for _ in range(20):
            result = CombatSystem.calculate_attack(attacker, defender)
            if result["hit"]:
                hits += 1
            defender.current_hp = 20  # Reset

        assert hits > 10, "Expected more hits with high DEX advantage"

    def test_unarmed_attack(self):
        """Verify attacks work without a weapon (base damage = 1)."""
        attacker = Character("Brawler")
        attacker.base_stats = Stats(strength=12, dexterity=50)

        defender = Character("Target")
        defender.base_stats = Stats(dexterity=5)

        result = CombatSystem.calculate_attack(attacker, defender)

        if result["hit"]:
            assert result["damage"] >= 1


# =============================================================================
# HELPER FUNCTION TESTS
# =============================================================================

class TestHelpers:
    """Test helper functions."""

    def test_create_enemy(self):
        """Verify create_enemy helper works."""
        goblin = create_enemy("Goblin", base_hp=15)

        assert goblin.name == "Goblin"
        assert goblin.current_hp == 15
        assert goblin.max_hp == 15


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestCombatIntegration:
    """Integration tests for full combat scenarios."""

    def test_full_combat_round(self):
        """Simulate a full combat encounter."""
        hero = Player("Hero", CharacterClass.FIGHTER)
        sword = Item("Iron Sword", ItemType.WEAPON, value=50, damage_min=6, damage_max=10)
        hero.equip(sword)

        goblin = create_enemy("Goblin", base_hp=15)

        rounds = 0
        max_rounds = 20

        while hero.current_hp > 0 and goblin.current_hp > 0 and rounds < max_rounds:
            CombatSystem.calculate_attack(hero, goblin)
            if goblin.current_hp <= 0:
                break
            CombatSystem.calculate_attack(goblin, hero)
            rounds += 1

        assert rounds < max_rounds, "Combat took too long"
        assert hero.current_hp < hero.max_hp or goblin.current_hp <= 0


# =============================================================================
# STANDALONE TEST RUNNER
# =============================================================================

def run_standalone_tests():
    """Run tests without pytest."""
    import traceback

    passed = 0
    failed = 0
    errors = []

    # Get all test classes
    test_classes = [
        TestStats, TestCharacter, TestHPClamping, TestPlayer,
        TestCombatSystem, TestHelpers, TestCombatIntegration
    ]

    for test_class in test_classes:
        instance = test_class()
        print(f"\n{test_class.__name__}:")

        for name in dir(instance):
            if name.startswith("test_"):
                try:
                    getattr(instance, name)()
                    print(f"  ✅ {name}")
                    passed += 1
                except AssertionError as e:
                    print(f"  ❌ {name}: {e}")
                    errors.append((name, str(e)))
                    failed += 1
                except Exception as e:
                    print(f"  ❌ {name}: {e}")
                    errors.append((name, traceback.format_exc()))
                    failed += 1

    print(f"\n{'='*60}")
    print(f"RESULTS: {passed} passed, {failed} failed")
    print(f"{'='*60}")

    return failed == 0


if __name__ == "__main__":
    try:
        import pytest
        pytest.main([__file__, "-v"])
    except ImportError:
        print("pytest not installed, running standalone tests...")
        success = run_standalone_tests()
        sys.exit(0 if success else 1)
