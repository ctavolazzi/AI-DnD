# Legacy Code

This folder contains old/deprecated code that has been replaced by newer implementations.

## Files

- **character.py**: Old Character class implementation. Replaced by the Character class in `dnd_game.py` which includes D&D 5e mechanics, inventory system, and combat abilities.

- **world.py**: Old Location/World class implementation. Replaced by the comprehensive world system in `world_builder.py` which includes the Emberpeak Region with 20+ locations, encounter tables, and NPCs.

- **game.py**: Old game loop implementation. Replaced by `dungeon_master.py` which orchestrates the full D&D game with AI narrative generation, quest system, and Obsidian integration.

- **game_state_manager.py**: Old game state management. Replaced by the integrated state management in `dungeon_master.py` and `game_manager.py`.

## Why These Were Moved

During architectural cleanup (see ARCHITECTURE_ANALYSIS.md), these duplicate classes were identified as causing conflicts:

1. Multiple incompatible Character class definitions
2. Multiple incompatible Location class definitions
3. No integration with current game systems

These files are preserved for reference but are not used by the active game system.

## Current System

The active D&D game system uses:
- `dnd_game.py`: Character class with D&D 5e mechanics and inventory
- `world_builder.py`: WorldManager with complete Emberpeak Region
- `dungeon_master.py`: Central game orchestrator
- `items.py`: Inventory and loot system
- `quest_system.py`: Quest tracking and objectives
