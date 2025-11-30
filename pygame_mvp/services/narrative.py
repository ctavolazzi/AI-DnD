"""
Narrative Service Wrapper

Wraps the existing narrative_engine.py for use in Pygame MVP.
"""

import sys
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class NarrativeService:
    """
    Wrapper for narrative engine integration.

    Provides narrative generation for scenes, combat, and dialogue.
    Falls back to simple text if narrative engine unavailable.
    """

    def __init__(self, use_ai: bool = False):
        self.use_ai = use_ai
        self._engine = None

        if use_ai:
            self._init_engine()

    def _init_engine(self) -> None:
        """Initialize the narrative engine."""
        try:
            from narrative_engine import NarrativeEngine
            self._engine = NarrativeEngine()
        except ImportError:
            print("Warning: narrative_engine not available, using fallback text")
            self._engine = None

    def describe_scene(self, location: str, characters: List[str]) -> str:
        """Generate scene description."""
        if self._engine and self.use_ai:
            return self._engine.describe_scene(location, characters)

        # Fallback
        char_list = ", ".join(characters) if characters else "no one"
        return f"You find yourself in {location}. Present: {char_list}."

    def describe_combat(
        self,
        attacker: str,
        defender: str,
        action: str,
        damage: Optional[int] = None
    ) -> str:
        """Generate combat description."""
        if self._engine and self.use_ai:
            return self._engine.describe_combat(attacker, defender, action, damage)

        # Fallback
        if damage:
            return f"{attacker} {action} {defender} for {damage} damage!"
        return f"{attacker} {action} {defender}!"

    def generate_quest(self, difficulty: str = "medium") -> str:
        """Generate a quest description."""
        if self._engine and self.use_ai:
            return self._engine.generate_quest(difficulty)

        # Fallback quests
        quests = {
            "easy": "Find the missing cat in the village outskirts.",
            "medium": "Clear the goblin camp threatening the trade route.",
            "hard": "Investigate the ancient ruins and defeat the necromancer within."
        }
        return quests.get(difficulty, quests["medium"])

    def handle_action(self, player: str, action: str, context: str) -> str:
        """Generate response to player action."""
        if self._engine and self.use_ai:
            return self._engine.handle_player_action(player, action, context)

        # Fallback
        return f"{player} attempts to {action}. The outcome is uncertain..."

    def generate_encounter(self, party_level: int, environment: str) -> str:
        """Generate random encounter."""
        if self._engine and self.use_ai:
            return self._engine.generate_random_encounter(party_level, environment)

        # Fallback
        encounters = [
            "A group of bandits emerges from the shadows!",
            "You hear growling in the darkness ahead...",
            "An ancient trap springs to life!",
            "A mysterious stranger approaches your party."
        ]
        import random
        return random.choice(encounters)

