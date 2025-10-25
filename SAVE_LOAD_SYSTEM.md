# Save/Load System for Python Game Scripts

Complete documentation for the game save/load functionality.

## Overview

The Python game scripts (`run_game.py`, `dungeon_master.py`) now support:
- **Autosave** after each turn
- **Resume** from saved games
- **Turn limits** enforced across sessions
- **Obsidian continuity** preserved

## Quick Start

### New Game (with autosave)
```bash
python3 run_game.py
# Autosaves to: saves/game_autosave.json after each turn
```

### Resume from Last Save
```bash
python3 run_game.py --resume saves/game_autosave.json
```

### List Available Saves
```bash
python3 run_game.py --list-saves
```

### Custom Save Location
```bash
python3 run_game.py --save-to saves/epic_campaign.json
```

## Files

| File | Purpose | Size |
|------|---------|------|
| `save_state.py` | Core functions: `save_game()`, `load_game()` | 6.7KB |
| `save_state_schema.json` | JSON schema definition | 2.7KB |
| `example_save.json` | Example save file | 2.7KB |
| `saves/` | Directory for save files (auto-created) | - |

## What Gets Saved

### ✅ Saved
- Current turn and turn limit
- Player characters (HP, attack, defense, status)
- Enemy characters (same)
- Current location
- Obsidian run ID and references
- Quest data
- Game start time

### ⚠️ NOT Saved (Limitation)
- Inventory items and equipment
- Learned spells
- Ability scores

**Why?** Keeps save files minimal (~3KB vs ~50KB). For 10-turn demo games, this is acceptable. For longer campaigns, extend the schema.

## Save File Format

```json
{
  "metadata": {
    "save_version": "1.0",
    "game_timestamp": "2025-10-25T17:35:42.123456",
    "current_turn": 3,
    "turn_limit": 10
  },
  "game_state": {
    "run_id": "20251025173000",
    "players": [
      {
        "name": "Azaroth",
        "char_class": "Warrior",
        "hp": 45,
        "max_hp": 50,
        "attack": 12,
        "defense": 8,
        "alive": true
      }
    ],
    "enemies": [...],
    "current_location": "Emberpeak Mountain Pass",
    "quest": {...},
    "obsidian_data": {...}
  }
}
```

## Command-Line Reference

### `run_game.py`

```bash
# Start new game
python3 run_game.py

# Resume from save
python3 run_game.py --resume saves/game.json

# Custom save location
python3 run_game.py --save-to saves/campaign_001.json

# List all saves
python3 run_game.py --list-saves

# Help
python3 run_game.py --help
```

## API Reference

### For Developers

```python
from save_state import save_game_to_file, load_game_from_file

# Save game
save_game_to_file(
    players=game.players,
    enemies=game.enemies,
    location=game.current_location,
    run_id="20251025_demo",
    current_turn=3,
    turn_limit=10,
    filepath="saves/game.json"
)

# Load game
state = load_game_from_file("saves/game.json")
# Returns dict with: players, enemies, location, run_id, current_turn, turn_limit
```

## Limitations & Future Work

### Current Limitations
1. **Inventory reset**: Loaded characters have "fresh" inventory
2. **Spells reset**: Spellbooks revert to class defaults
3. **Ability scores reset**: Regenerated from class templates

### Why These Limits?
- **Simplicity**: 3KB save files vs 50KB
- **Demo games**: 10-turn sessions don't need full persistence
- **Obsidian**: Narrative progression tracked separately

### Future Extensions (v1.1)
- [ ] Save inventory items and equipment
- [ ] Save learned spells
- [ ] Save ability scores and proficiency
- [ ] Schema versioning for backwards compatibility

## Troubleshooting

### "Save file not found"
```bash
# Check if save exists
ls -la saves/

# List available saves
python3 run_game.py --list-saves
```

### "Corrupted save file"
```bash
# Validate JSON
python3 -m json.tool saves/game.json

# Start new game (old save lost)
python3 run_game.py --save-to saves/game_new.json
```

### "Turn limit exceeded"
Save files enforce turn limits. If `current_turn > turn_limit`, the save is invalid.

Solution: Edit the JSON file to increase `turn_limit` or start a new game.

## Architecture

### Design Decisions

| Decision | Reasoning |
|----------|-----------|
| JSON not SQL | Standalone scripts, no server required |
| Minimal schema | Fast load/save, human-readable |
| Autosave each turn | Natural checkpoint, no data loss |
| Skip inventory | Keeps files small for demos |

### Integration Points

1. **run_game.py line 13**: Import save functions
2. **run_game.py line 32**: `reconstruct_character()` helper
3. **run_game.py line 226**: Modified function signature
4. **run_game.py line 247**: Resume logic
5. **run_game.py line 318**: Reconstruct game objects
6. **run_game.py line 657**: Autosave after each turn
7. **run_game.py line 727**: Command-line arg parsing

## Examples

### Scenario 1: Save at Turn 3, Resume Later
```bash
# Start game (autosaves after turn 3)
python3 run_game.py

# Later...
python3 run_game.py --resume saves/game_autosave.json
# Continues from turn 4
```

### Scenario 2: Multiple Save Slots
```bash
# Campaign 1
python3 run_game.py --save-to saves/campaign_001.json

# Campaign 2
python3 run_game.py --save-to saves/campaign_002.json

# List both
python3 run_game.py --list-saves
```

### Scenario 3: Backup Before Risky Combat
```bash
# Backup current save
cp saves/game_autosave.json saves/backup_turn_5.json

# If combat goes badly, restore
python3 run_game.py --resume saves/backup_turn_5.json
```

## Related Documentation

- **AGENTS.md**: AI agent instructions
- **README.md**: Project overview
- **backend/SETUP.md**: Backend API setup
- **_work_efforts_/10-19_development/10_core/10.13_game_save_load_system.md**: Work effort tracking

## FAQ

**Q: Will this work with dungeon_master.py?**
A: Not yet. Currently integrated into `run_game.py` only. Extending to `dungeon_master.py` is future work.

**Q: Can I edit save files manually?**
A: Yes! They're JSON. Edit carefully and validate with `python3 -m json.tool`.

**Q: What about the web frontend?**
A: Web frontend already uses `localStorage` for saves. This system is for Python scripts only.

**Q: Can I convert saves to SQL?**
A: Yes, but not implemented. See SQL_CONVERSION_GUIDE.md (if you have it) for details.

---

**Status**: ✅ Production-ready for Python game scripts
**Version**: 1.0
**Last Updated**: 2025-10-25



