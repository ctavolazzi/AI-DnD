# AI-DnD Codebase Exploration

## Overview

AI-DnD is a text-based Dungeons & Dragons simulator that combines traditional role-playing game mechanics with AI-powered narrative generation. This document tracks our exploration and understanding of the codebase as we delve deeper into its architecture, features, and potential areas for enhancement.

## Core Architecture

### Game Engine Components

1. **DnDGame (dnd_game.py)**
   - Central game engine managing characters, combat, and game state
   - Handles turn progression and game conditions
   - Implements core game mechanics

2. **Character System**
   - Character classes in `dnd_game.py` (gameplay) and `character.py` (persistence)
   - Class-specific abilities (Fighter, Wizard, Rogue, Cleric, etc.)
   - Status effects, damage calculation, and character state management

3. **NarrativeEngine (narrative_engine.py)**
   - Uses Ollama for AI-powered narrative generation
   - Creates scene descriptions, dialogue, quests, and combat summaries
   - Uses a "mistral" model by default with concise DM-style prompts

4. **World System (world.py)**
   - Manages locations, connections, and world navigation
   - Configuration-based approach to world definition
   - Location descriptions and movement mechanics

5. **Game Display (rich_game_display_integration.py)**
   - Uses the Rich library for terminal UI
   - Displays character stats, combat logs, and game progression
   - Real-time updating interface

### Game Flow

1. Initialization through main.py or run_game.py
2. Character creation (players and enemies)
3. Quest generation by the narrative engine
4. Turn-based progression:
   - Scene descriptions
   - Combat interactions
   - Random encounters
   - Turn summaries
5. Game conclusion after predetermined turns or when all players/enemies are defeated

## Technical Features

1. **Modular Architecture**: Separate modules for different functionality
2. **AI Integration**: Ollama for narrative content generation
3. **Rich Terminal UI**: Visually appealing interface
4. **Logging System**: Comprehensive logging for debugging and game events
5. **Configuration-Based Design**: Config files define world elements

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

The project relies on several Python libraries:
- Rich (terminal UI)
- Ollama (AI integration)
- OpenAI (potential alternative AI integration)
- Various utility libraries

## Development Status

The project appears to be a fairly complete D&D simulator with:
- Character creation and management
- Combat system with abilities
- AI-powered narrative generation
- World navigation
- Visual display

## Key Observations

1. The narrative engine uses local Ollama models which allows for offline gameplay
2. The combat system includes abilities specific to character classes
3. The game uses a turn-based approach with a maximum number of turns
4. The project leverages Rich for terminal-based UI rather than a graphical interface
5. Configuration is used to define world elements like locations

## Next Steps for Exploration

- Investigate test files to understand testing strategy
- Examine the self-playing game capabilities
- Look at the narrative engine's interaction with Ollama
- Study the Rich display integration for UI enhancements
- Review the logging system for debugging capabilities

---

*This document will be updated as we continue to explore the codebase.*