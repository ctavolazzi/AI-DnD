"""
Minimal save/load utilities for D&D game scripts.

Design Philosophy:
- Two functions: save_game() and load_game()
- JSON-based (human-readable, zero deps)
- Integrated at turn boundaries
- Preserves Obsidian continuity

Usage:
    # Save after each turn
    save_game_to_file(
        players=game.players,
        enemies=game.enemies,
        location=game.current_location,
        run_id=run_id,
        current_turn=turn_count,
        turn_limit=max_turns,
        filepath="saves/game_001.json"
    )

    # Resume on startup
    state = load_game_from_file("saves/game_001.json")
    # Returns dict with: players, enemies, location, run_id, current_turn, turn_limit
"""

import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


def save_game_to_file(
    players: List[Any],
    enemies: List[Any],
    location: str,
    run_id: str,
    current_turn: int,
    turn_limit: int,
    filepath: str = "game_save.json",
    quest_data: Optional[Dict] = None,
    obsidian_data: Optional[Dict] = None,
    start_time: Optional[str] = None,
    random_seed: Optional[int] = None
) -> None:
    """
    Save game state to JSON file.

    Args:
        players: List of player Character objects
        enemies: List of enemy Character objects (can be empty)
        location: Current location string
        run_id: Obsidian vault run ID
        current_turn: Current turn number (0-based)
        turn_limit: Maximum turns allowed
        filepath: Where to save (default: game_save.json)
        quest_data: Optional quest information
        obsidian_data: Optional Obsidian vault references
        start_time: Optional game start timestamp
        random_seed: Optional random seed for reproducibility

    Raises:
        ValueError: If current_turn > turn_limit (invalid state)
        IOError: If file cannot be written
    """
    # Validation
    if current_turn > turn_limit:
        raise ValueError(
            f"Invalid state: current_turn ({current_turn}) exceeds "
            f"turn_limit ({turn_limit})"
        )

    # Serialize characters (handle both dict and object attributes)
    def serialize_character(char) -> Dict:
        """Convert Character object to dict."""
        if isinstance(char, dict):
            return char
        return {
            "name": char.name,
            "char_class": getattr(char, 'char_class', 'Unknown'),
            "hp": char.hp,
            "max_hp": char.max_hp,
            "attack": char.attack,
            "defense": char.defense,
            "alive": char.alive,
            "abilities": getattr(char, 'abilities', {}),
            "status_effects": getattr(char, 'status_effects', [])
        }

    # Build save data
    save_data = {
        "metadata": {
            "save_version": "1.0",
            "game_timestamp": datetime.datetime.now().isoformat(),
            "current_turn": current_turn,
            "turn_limit": turn_limit
        },
        "game_state": {
            "run_id": run_id,
            "status": "active",
            "start_time": start_time or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "players": [serialize_character(p) for p in players],
            "enemies": [serialize_character(e) for e in enemies],
            "current_location": location
        }
    }

    # Add optional data
    if random_seed is not None:
        save_data["metadata"]["python_seed"] = random_seed

    if quest_data:
        save_data["game_state"]["quest"] = quest_data

    if obsidian_data:
        save_data["game_state"]["obsidian_data"] = obsidian_data

    # Create directory if needed
    save_path = Path(filepath)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Write to file
    with open(save_path, 'w') as f:
        json.dump(save_data, f, indent=2)

    print(f"💾 Game saved to {filepath} (Turn {current_turn}/{turn_limit})")


def load_game_from_file(filepath: str = "game_save.json") -> Dict[str, Any]:
    """
    Load game state from JSON file.

    Args:
        filepath: Path to save file (default: game_save.json)

    Returns:
        Dictionary with keys:
        - players: List[Dict] - Player character data
        - enemies: List[Dict] - Enemy character data
        - location: str - Current location
        - run_id: str - Obsidian run ID
        - current_turn: int - Current turn number
        - turn_limit: int - Maximum turns
        - start_time: str - Original game start time
        - quest_data: Optional[Dict] - Quest information
        - obsidian_data: Optional[Dict] - Obsidian references
        - random_seed: Optional[int] - Random seed if saved

    Raises:
        FileNotFoundError: If save file doesn't exist
        ValueError: If save file is corrupted or invalid
    """
    save_path = Path(filepath)

    if not save_path.exists():
        raise FileNotFoundError(f"Save file not found: {filepath}")

    # Load JSON
    try:
        with open(save_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Corrupted save file: {e}")

    # Validate structure
    if "metadata" not in data or "game_state" not in data:
        raise ValueError("Invalid save file: missing required sections")

    metadata = data["metadata"]
    game_state = data["game_state"]

    # Extract data
    result = {
        "players": game_state.get("players", []),
        "enemies": game_state.get("enemies", []),
        "location": game_state.get("current_location", "Unknown"),
        "run_id": game_state.get("run_id", ""),
        "current_turn": metadata.get("current_turn", 0),
        "turn_limit": metadata.get("turn_limit", 10),
        "start_time": game_state.get("start_time"),
        "quest_data": game_state.get("quest"),
        "obsidian_data": game_state.get("obsidian_data"),
        "random_seed": metadata.get("python_seed")
    }

    # Validate turn constraint
    if result["current_turn"] > result["turn_limit"]:
        raise ValueError(
            f"Invalid save: turn {result['current_turn']} exceeds "
            f"limit {result['turn_limit']}"
        )

    print(f"📂 Game loaded from {filepath} (Turn {result['current_turn']}/{result['turn_limit']})")

    return result


def list_save_files(directory: str = ".") -> List[str]:
    """
    List all save files in a directory.

    Args:
        directory: Directory to search (default: current)

    Returns:
        List of save file paths (sorted by modification time, newest first)
    """
    save_dir = Path(directory)
    if not save_dir.exists():
        return []

    # Find all .json files
    save_files = list(save_dir.glob("*.json"))

    # Filter to valid saves (have metadata section)
    valid_saves = []
    for filepath in save_files:
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if "metadata" in data and "game_state" in data:
                    valid_saves.append(filepath)
        except (json.JSONDecodeError, IOError):
            continue

    # Sort by modification time (newest first)
    valid_saves.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return [str(p) for p in valid_saves]


if __name__ == "__main__":
    """Demo usage"""
    print("=== Save/Load System Demo ===\n")

    # Mock character data
    class MockCharacter:
        def __init__(self, name, hp, max_hp):
            self.name = name
            self.char_class = "Warrior"
            self.hp = hp
            self.max_hp = max_hp
            self.attack = 10
            self.defense = 5
            self.alive = hp > 0
            self.abilities = {"power_attack": True}
            self.status_effects = []

    # Create mock game state
    players = [
        MockCharacter("Azaroth", 45, 50),
        MockCharacter("Luna", 30, 40)
    ]
    enemies = [
        MockCharacter("Goblin", 15, 20)
    ]

    # Save game
    print("Saving game...")
    save_game_to_file(
        players=players,
        enemies=enemies,
        location="Dark Forest",
        run_id="20251025_demo",
        current_turn=3,
        turn_limit=10,
        filepath="demo_save.json",
        quest_data={"name": "Defeat the Dark Lord", "status": "Active"}
    )

    # Load game
    print("\nLoading game...")
    loaded = load_game_from_file("demo_save.json")

    print(f"\n✅ Loaded state:")
    print(f"   Run ID: {loaded['run_id']}")
    print(f"   Turn: {loaded['current_turn']}/{loaded['turn_limit']}")
    print(f"   Location: {loaded['location']}")
    print(f"   Players: {len(loaded['players'])}")
    print(f"   Enemies: {len(loaded['enemies'])}")
    print(f"   Quest: {loaded['quest_data']['name']}")

    # Cleanup
    Path("demo_save.json").unlink()
    print("\n✅ Demo complete!")



