"""
Save/Load System

Handles game state persistence with:
- Auto-save functionality
- Multiple save slots
- Save file validation
- Backup system
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class SaveMetadata:
    """Metadata about a save file."""
    slot: int
    name: str
    player_name: str
    player_level: int
    location: str
    playtime_seconds: int
    turn_count: int
    created_at: str
    updated_at: str
    version: str = "1.0.0"

    @property
    def playtime_formatted(self) -> str:
        """Format playtime as HH:MM:SS."""
        hours = self.playtime_seconds // 3600
        minutes = (self.playtime_seconds % 3600) // 60
        seconds = self.playtime_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class SaveSystem:
    """
    Manages game saves and loads.
    """

    SAVE_VERSION = "1.0.0"
    MAX_SLOTS = 5

    def __init__(self, save_directory: str = "saves"):
        self.save_directory = Path(save_directory)
        self.save_directory.mkdir(parents=True, exist_ok=True)
        self.backup_directory = self.save_directory / "backups"
        self.backup_directory.mkdir(exist_ok=True)

    def _get_save_path(self, slot: int) -> Path:
        """Get path for a save slot."""
        return self.save_directory / f"save_{slot}.json"

    def _get_backup_path(self, slot: int) -> Path:
        """Get path for a backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.backup_directory / f"save_{slot}_backup_{timestamp}.json"

    def _calculate_checksum(self, data: str) -> str:
        """Calculate checksum for save data integrity."""
        return hashlib.md5(data.encode()).hexdigest()

    def save_game(
        self,
        slot: int,
        save_name: str,
        game_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save game to a slot.

        Args:
            slot: Save slot number (1-5)
            save_name: Display name for the save
            game_data: The actual game state to save
            metadata: Additional metadata (player info, etc.)

        Returns:
            True if save was successful
        """
        if not 1 <= slot <= self.MAX_SLOTS:
            return False

        save_path = self._get_save_path(slot)

        # Backup existing save
        if save_path.exists():
            self._create_backup(slot)

        # Build save structure
        now = datetime.now().isoformat()

        save_data = {
            "version": self.SAVE_VERSION,
            "slot": slot,
            "name": save_name,
            "created_at": metadata.get("created_at", now) if metadata else now,
            "updated_at": now,
            "metadata": metadata or {},
            "game_data": game_data
        }

        # Calculate checksum
        json_str = json.dumps(save_data, sort_keys=True)
        save_data["checksum"] = self._calculate_checksum(json_str)

        try:
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save game: {e}")
            return False

    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Load game from a slot.

        Returns:
            Game data dict or None if load failed
        """
        save_path = self._get_save_path(slot)

        if not save_path.exists():
            return None

        try:
            with open(save_path, 'r') as f:
                save_data = json.load(f)

            # Verify checksum
            stored_checksum = save_data.pop("checksum", None)
            json_str = json.dumps(save_data, sort_keys=True)
            calculated_checksum = self._calculate_checksum(json_str)

            if stored_checksum and stored_checksum != calculated_checksum:
                print("Warning: Save file may be corrupted (checksum mismatch)")
                # Still try to load, but warn

            return save_data
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None

    def delete_save(self, slot: int) -> bool:
        """Delete a save slot."""
        save_path = self._get_save_path(slot)

        if save_path.exists():
            # Create backup before delete
            self._create_backup(slot)
            save_path.unlink()
            return True
        return False

    def _create_backup(self, slot: int) -> bool:
        """Create a backup of a save slot."""
        save_path = self._get_save_path(slot)
        backup_path = self._get_backup_path(slot)

        if save_path.exists():
            try:
                import shutil
                shutil.copy2(save_path, backup_path)
                return True
            except Exception:
                return False
        return False

    def get_save_info(self, slot: int) -> Optional[SaveMetadata]:
        """Get metadata about a save slot without loading full game data."""
        save_data = self.load_game(slot)
        if not save_data:
            return None

        metadata = save_data.get("metadata", {})
        return SaveMetadata(
            slot=slot,
            name=save_data.get("name", "Unknown"),
            player_name=metadata.get("player_name", "Hero"),
            player_level=metadata.get("player_level", 1),
            location=metadata.get("location", "Unknown"),
            playtime_seconds=metadata.get("playtime_seconds", 0),
            turn_count=metadata.get("turn_count", 0),
            created_at=save_data.get("created_at", ""),
            updated_at=save_data.get("updated_at", ""),
            version=save_data.get("version", "1.0.0")
        )

    def get_all_saves(self) -> Dict[int, Optional[SaveMetadata]]:
        """Get info for all save slots."""
        saves = {}
        for slot in range(1, self.MAX_SLOTS + 1):
            saves[slot] = self.get_save_info(slot)
        return saves

    def has_any_saves(self) -> bool:
        """Check if any saves exist."""
        return any(self.get_save_info(slot) for slot in range(1, self.MAX_SLOTS + 1))

    def get_latest_save(self) -> Optional[int]:
        """Get the most recently updated save slot."""
        saves = self.get_all_saves()
        latest_slot = None
        latest_time = None

        for slot, metadata in saves.items():
            if metadata:
                if latest_time is None or metadata.updated_at > latest_time:
                    latest_time = metadata.updated_at
                    latest_slot = slot

        return latest_slot

    def cleanup_old_backups(self, keep_count: int = 5) -> int:
        """
        Clean up old backups, keeping only the most recent ones.
        Returns number of backups deleted.
        """
        deleted = 0

        for slot in range(1, self.MAX_SLOTS + 1):
            pattern = f"save_{slot}_backup_*.json"
            backups = sorted(
                self.backup_directory.glob(pattern),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )

            # Delete old backups
            for backup in backups[keep_count:]:
                backup.unlink()
                deleted += 1

        return deleted


# =============================================================================
# GAME STATE SERIALIZATION
# =============================================================================

class GameStateSerializer:
    """
    Helper class to serialize/deserialize game state.
    """

    @staticmethod
    def serialize_character(character) -> dict:
        """Serialize a character to dict."""
        return {
            "name": character.name,
            "char_class": character.char_class,
            "level": getattr(character, "level", 1),
            "xp": getattr(character, "xp", 0),
            "hp": character.hp,
            "max_hp": character.max_hp,
            "mana": getattr(character, "mana", 0),
            "max_mana": getattr(character, "max_mana", 0),
            "attack": character.attack,
            "defense": character.defense,
            "alive": character.alive,
            # Equipment
            "equipment": {
                slot.value: {
                    "name": eq.name,
                    "rarity": eq.rarity
                } if eq else None
                for slot, eq in getattr(character, "equipped", {}).items()
            } if hasattr(character, "equipped") else {},
            # Abilities
            "abilities": [
                ability.name for ability in getattr(character, "abilities", [])
            ],
            # Status effects
            "status_effects": [
                {
                    "type": status.status_type.value,
                    "duration": status.duration,
                    "power": status.power
                }
                for status in getattr(character, "status_effects", [])
            ]
        }

    @staticmethod
    def serialize_inventory(inventory) -> dict:
        """Serialize inventory to dict."""
        return {
            "gold": inventory.gold,
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "item_type": item.item_type.value
                }
                for item in inventory.items
            ]
        }

    @staticmethod
    def serialize_game_state(game_state, quest_tracker=None, playtime_seconds=0) -> dict:
        """
        Serialize complete game state.
        """
        data = {
            "turn_count": game_state.turn_count,
            "phase": game_state.phase.value,
            "location": {
                "name": game_state.location.name,
                "description": game_state.location.description,
                "exits": game_state.location.exits,
                "npcs": game_state.location.npcs
            },
            "players": [
                GameStateSerializer.serialize_character(p)
                for p in game_state.players
            ],
            "enemies": [
                GameStateSerializer.serialize_character(e)
                for e in game_state.enemies
            ],
            "inventory": GameStateSerializer.serialize_inventory(game_state.inventory),
            "adventure_log": game_state.adventure_log[-100:],  # Keep last 100 entries
            "stats": {
                "enemies_killed": getattr(game_state, "enemies_killed", 0),
                "gold_earned": getattr(game_state, "gold_earned", 0),
                "damage_dealt": getattr(game_state, "damage_dealt", 0),
                "damage_taken": getattr(game_state, "damage_taken", 0),
                "playtime_seconds": playtime_seconds
            }
        }

        # Add quest data if tracker provided
        if quest_tracker:
            data["quests"] = quest_tracker.to_dict()

        return data

    @staticmethod
    def get_save_metadata(game_state, playtime_seconds=0) -> dict:
        """Get metadata for save file."""
        player = game_state.get_current_player()
        return {
            "player_name": player.name if player else "Unknown",
            "player_level": getattr(player, "level", 1) if player else 1,
            "location": game_state.location.name,
            "playtime_seconds": playtime_seconds,
            "turn_count": game_state.turn_count
        }


# =============================================================================
# AUTO-SAVE MANAGER
# =============================================================================

class AutoSaveManager:
    """
    Manages automatic saving.
    """

    def __init__(self, save_system: SaveSystem, auto_save_slot: int = 1):
        self.save_system = save_system
        self.auto_save_slot = auto_save_slot
        self.save_interval_turns = 10  # Auto-save every N turns
        self.last_save_turn = 0
        self.enabled = True

    def check_auto_save(
        self,
        current_turn: int,
        game_state,
        quest_tracker=None,
        playtime_seconds=0
    ) -> bool:
        """
        Check if auto-save should trigger and perform it.
        Returns True if auto-save was performed.
        """
        if not self.enabled:
            return False

        if current_turn - self.last_save_turn >= self.save_interval_turns:
            return self.perform_auto_save(game_state, quest_tracker, playtime_seconds)

        return False

    def perform_auto_save(
        self,
        game_state,
        quest_tracker=None,
        playtime_seconds=0
    ) -> bool:
        """Perform an auto-save."""
        game_data = GameStateSerializer.serialize_game_state(
            game_state, quest_tracker, playtime_seconds
        )
        metadata = GameStateSerializer.get_save_metadata(game_state, playtime_seconds)

        success = self.save_system.save_game(
            slot=self.auto_save_slot,
            save_name="Auto-Save",
            game_data=game_data,
            metadata=metadata
        )

        if success:
            self.last_save_turn = game_state.turn_count

        return success

