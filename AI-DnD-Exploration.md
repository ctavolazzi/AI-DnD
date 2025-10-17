# AI-DnD Codebase Exploration

## Overview

AI-DnD is a text-based Dungeons & Dragons simulator that combines traditional role-playing game mechanics with AI-powered narrative generation. This document tracks our exploration and understanding of the codebase as we delve deeper into its architecture, features, and potential areas for enhancement.

## Core Architecture

### Runtime Orchestration

1. **Main Entrypoint (`main.py`)**
   - Parses CLI arguments (vault path, reset flag, model choice, etc.).
   - Sets up logging and optionally resets the target Obsidian vault.
   - Instantiates `DungeonMaster` and drives the overall run via `DungeonMaster.run_game()`.

2. **DungeonMaster (`dungeon_master.py`)**
   - Coordinates the high-level game lifecycle for a single Obsidian vault.
   - Initializes run metadata, the `GameEventManager`, `GameManager`, and `DnDGame` engine.
   - Persists run state to `Current Run.md` and orchestrates event propagation to Obsidian.

3. **Game Loop (`run_game.py` / `dnd_game.py`)**
   - `DnDGame` encapsulates combat resolution, character stats, and AI turns.
   - Uses `NarrativeEngine` for moment-to-moment descriptions and quest content.
   - Raises `GameError` for invalid operations (e.g., unknown classes, bad combat inputs).

### Supporting Systems

1. **Character & State Models**
   - `dnd_game.Character` contains combat stats and abilities.
   - `character.py`, `character_state.py`, and `game_state.py` persist campaign entities and runtime snapshots.
   - `game_state_manager.py` offers higher-level helpers for saving/restoring state.

2. **Narrative & AI Integration (`narrative_engine.py`)**
   - Wraps Ollama CLI calls with a compact system prompt (“15 words max” style direction).
   - Provides helpers for scenes, combat, encounters, quests, dialogue, and conclusions.
   - Falls back to a generic string if the Ollama invocation fails.

3. **Event Propagation (`game_event_manager.py`)**
   - Publishes structured events from the game loop.
   - Keeps `run_data` in sync and triggers `DungeonMaster.update_current_run()` after each event.
   - Allows other components to subscribe to granular event types.

4. **World & Modules**
   - `world.py` defines tile-based navigation and adjacency.
   - `module_loader.py` supplies a minimal plug-in loader for optional rules modules.
   - Modules currently default to placeholders, suggesting a future extension point.

5. **Presentation Layers**
   - `rich_game_display.py` and `rich_game_display_integration.py` integrate with the Rich TUI toolkit.
   - `obsidian_logger.py` writes Markdown artefacts (characters, quests, sessions, etc.) into the vault.
   - `JournalManager` and `game_manager.py` craft per-character journals and maintain knowledge graphs.

### Game Flow

1. **Launch**
   - `main.py` ensures the vault exists, optionally wipes it, and prints execution metadata.
   - `DungeonMaster.initialize_run()` seeds `current_run_data` (run id, timestamps, quest placeholders).

2. **Setup**
   - `GameManager` subscribes to core events (character/location/quest/item updates).
   - `ObsidianLogger` provisions directories (`Characters/`, `Events/`, `Runs/`, etc.) and templates.

3. **Turn Loop**
   - `DnDGame.run_turn()` (via `DungeonMaster.run_game`) updates characters, resolves combat, and posts events.
   - `NarrativeEngine` generates narration for scenes, actions, and outcomes.
   - `GameEventManager.publish()` pushes updates into `Current Run.md` and knowledge graphs in real time.

4. **Completion**
   - Upon success or failure, `DungeonMaster` marks the run status and writes summaries to the vault.
   - Error handling routes through `error_logger.py` for structured logging.

## Technical Features

1. **Obsidian-First Logging** – Markdown artefacts with YAML frontmatter + backlink-friendly links.
2. **Knowledge Graph** – `GameManager` tracks awareness/relationships between entities (theory-of-mind light).
3. **Autonomous Journaling** – `JournalManager` generates per-character diaries and “thoughts” entries.
4. **Extensible Modules** – Loader infrastructure available for house rules and experimental mechanics.
5. **Rich Terminal UI** – Optional live display for combat stats using the `rich` library.

## Project Structure

```
/
├── main.py                         # Main application entry point
├── run_game.py                     # Game launcher
├── dnd_game.py                     # Core game engine
├── narrative_engine.py             # AI-powered narrative generation
├── rich_game_display_integration.py # Terminal UI display
├── character.py                    # Character persistence model
├── world.py                        # World and location management
├── config.py                       # Game configuration
├── requirements.txt                # Project dependencies
└── ...                             # Additional supporting files
```

## Dependencies

- **Core**: `jinja2`, `pytest`, `pydantic`, `python-dateutil`, etc. (see `requirements.txt`).
- **UI**: `rich` (required by `rich_game_display*` modules — missing in the default environment).
- **AI**: Local Ollama binary accessible via CLI for `NarrativeEngine`.
- **File IO**: Relies on standard library modules for filesystem orchestration.

## Development Status

The project appears to be a fairly complete D&D simulator with:
- Character creation and management
- Combat system with abilities
- AI-powered narrative generation
- World navigation
- Visual display

## Key Observations

1. Vault writes are central—almost every subsystem eventually funnels data through `ObsidianLogger`.
2. Many modules assume synchronous filesystem access; async runtimes would require refactors.
3. Narrative generation is intentionally terse (≤15 words), hinting at log-friendly summaries.
4. Several tests depend on the `rich` package, so installing UI dependencies is necessary before running the suite.
5. Module infrastructure exists but currently has minimal implementations, leaving room for custom content packs.

## Testing Notes

- `pytest` currently fails during collection because `rich` is not installed (`ModuleNotFoundError`).
- Most tests target journal creation, DM journaling, narrative pipelines, and logging consistency.
- Installing the optional UI dependency should unblock the Rich display tests.

---

*This document will be updated as we continue to explore the codebase.*