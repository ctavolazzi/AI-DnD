"""
Stats Adapter - Bridge between game stats and D&D UI display.

The game uses 4 core stats (STR, DEX, INT, CON).
D&D UIs expect 6 stats (STR, DEX, CON, INT, WIS, CHA).

This adapter:
1. Maps the 4 core stats to D&D equivalents
2. Derives WIS and CHA from character data and class
3. Calculates derived values (AC, initiative, modifiers)
4. Formats data for PixelInventoryScreen display
"""

from dataclasses import dataclass
from typing import Dict, Optional
from pygame_mvp.game.systems import Character, Stats, CharacterClass


@dataclass
class D20Stats:
    """Full 6-attribute D&D stat block with derived values."""

    # Core attributes (10 = average)
    strength: int = 10
    dexterity: int = 10
    constitution: int = 10
    intelligence: int = 10
    wisdom: int = 10
    charisma: int = 10

    # Derived values
    ac: int = 10  # Armor class
    initiative: int = 0
    proficiency_bonus: int = 2

    def modifier(self, stat_value: int) -> int:
        """Calculate D20 modifier from stat value.

        10-11 = +0
        12-13 = +1
        14-15 = +2
        etc.
        """
        return (stat_value - 10) // 2

    def get_modifier(self, stat_name: str) -> int:
        """Get modifier for a specific stat."""
        stat_value = getattr(self, stat_name.lower(), 10)
        return self.modifier(stat_value)

    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for UI display."""
        return {
            "STR": self.strength,
            "DEX": self.dexterity,
            "CON": self.constitution,
            "INT": self.intelligence,
            "WIS": self.wisdom,
            "CHA": self.charisma,
            "AC": self.ac,
            "Initiative": self.initiative,
            "Proficiency": self.proficiency_bonus,
        }


class StatsAdapter:
    """
    Converts game Character stats to D&D UI-compatible format.

    Usage:
        character = Character("Aragorn", level=5)
        adapter = StatsAdapter(character)
        d20_stats = adapter.get_d20_stats()

        # Display in UI
        inventory_screen.set_stats(d20_stats)
    """

    # Define base stats for each class
    CLASS_BASE_STATS = {
        CharacterClass.FIGHTER: {
            "str_bonus": 2,
            "dex_penalty": -1,
            "con_bonus": 1,
            "wis_base": 10,
            "cha_base": 10,
        },
        CharacterClass.WIZARD: {
            "str_penalty": -1,
            "dex_base": 10,
            "int_bonus": 2,
            "con_penalty": -1,
            "wis_bonus": 1,
            "cha_base": 10,
        },
        CharacterClass.ROGUE: {
            "str_base": 10,
            "dex_bonus": 2,
            "int_base": 10,
            "con_base": 10,
            "wis_penalty": -1,
            "cha_bonus": 1,
        },
        CharacterClass.CLERIC: {
            "str_base": 10,
            "dex_base": 10,
            "con_bonus": 1,
            "int_base": 10,
            "wis_bonus": 2,
            "cha_base": 10,
        },
    }

    def __init__(self, character: Character):
        self.character = character
        self.d20_stats: Optional[D20Stats] = None
        self._compute_stats()

    def _compute_stats(self) -> None:
        """Compute full D&D stat block from character data."""
        base = self.character.base_stats
        char_class = getattr(self.character, 'char_class', CharacterClass.FIGHTER)

        # Start with core stats
        stats = D20Stats(
            strength=base.strength,
            dexterity=base.dexterity,
            constitution=base.constitution,
            intelligence=base.intelligence,
        )

        # Add WIS and CHA based on class
        class_config = self.CLASS_BASE_STATS.get(char_class, {})
        stats.wisdom = class_config.get("wis_base", 10)
        stats.charisma = class_config.get("cha_base", 10)

        # Apply any class-based stat adjustments
        for stat_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            bonus_key = f"{stat_name[:3]}_bonus"
            penalty_key = f"{stat_name[:3]}_penalty"

            if bonus_key in class_config:
                current = getattr(stats, stat_name)
                setattr(stats, stat_name, current + class_config[bonus_key])

            if penalty_key in class_config:
                current = getattr(stats, stat_name)
                setattr(stats, stat_name, current + class_config[penalty_key])

        # Compute derived values
        stats.ac = 10 + stats.get_modifier("dexterity")
        stats.initiative = stats.get_modifier("dexterity")
        stats.proficiency_bonus = 2 + (self.character.level // 4)

        self.d20_stats = stats

    def get_d20_stats(self) -> D20Stats:
        """Get the computed D&D stat block."""
        if self.d20_stats is None:
            self._compute_stats()
        return self.d20_stats

    def get_stats_dict(self) -> Dict[str, int]:
        """Get stats as a simple dictionary."""
        return self.get_d20_stats().to_dict()

    def get_stat_display_lines(self) -> list:
        """Format stats for text display (like character sheet overlay)."""
        stats = self.get_d20_stats()
        lines = [
            f"STR: {stats.strength} ({stats.get_modifier('strength'):+d})",
            f"DEX: {stats.dexterity} ({stats.get_modifier('dexterity'):+d})",
            f"CON: {stats.constitution} ({stats.get_modifier('constitution'):+d})",
            f"INT: {stats.intelligence} ({stats.get_modifier('intelligence'):+d})",
            f"WIS: {stats.wisdom} ({stats.get_modifier('wisdom'):+d})",
            f"CHA: {stats.charisma} ({stats.get_modifier('charisma'):+d})",
            "",
            f"AC: {stats.ac}",
            f"Initiative: {stats.initiative:+d}",
            f"Proficiency: +{stats.proficiency_bonus}",
        ]
        return lines

    def update_from_character(self) -> None:
        """Refresh stats if character has changed."""
        self.d20_stats = None
        self._compute_stats()


# Example usage and test
if __name__ == "__main__":
    # Create a test character
    character = Character("Test Fighter", level=5, max_hp=30)
    character.char_class = CharacterClass.FIGHTER
    character.base_stats = Stats(strength=14, dexterity=10, intelligence=8, constitution=14)

    # Create adapter
    adapter = StatsAdapter(character)

    # Get D&D stats
    d20_stats = adapter.get_d20_stats()

    # Display
    print("=== Fighter Stats ===")
    for line in adapter.get_stat_display_lines():
        print(line)

    print("\n=== Stat Dictionary ===")
    print(adapter.get_stats_dict())
