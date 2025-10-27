# Pygame D&D Game

A graphical version of the AI-DnD game built with pygame, preserving all the original game mechanics while adding a visual interface.

## Features

- **Complete D&D Mechanics**: All original game features preserved (combat, spells, inventory, character progression)
- **Visual Interface**: 1200x800 pygame window with D&D-themed UI
- **Character Display**: Health/mana bars, stats, and character information
- **Interactive UI**: Clickable buttons for game actions
- **Real-time Updates**: UI updates automatically as game state changes
- **Modular Design**: Clean separation between game logic and presentation

## Installation

1. Install pygame:
```bash
pip install pygame
```

2. Run the game:
```bash
python3 pygame_dnd_game.py
```

## Usage

### Command Line Options

```bash
python3 pygame_dnd_game.py [options]

Options:
  --vault VAULT     Path to Obsidian vault (default: character-journal-test-vault)
  --reset          Reset the vault before running
  --turns TURNS    Number of turns to run (default: 10)
  --model MODEL    Model to use for generation (default: mistral)
```

### Game Interface

The game window is divided into several panels:

- **Game Log** (left): Shows current quest, turn information, and game events
- **Character Panels** (right): Display player and enemy stats with health/mana bars
- **Status Panel** (bottom left): Shows current game state
- **Inventory Panel** (right): Lists player items
- **Spell Panel** (right): Shows known spells and mana costs
- **Quest Panel** (right): Displays current objectives

### Controls

- **Next Turn**: Advance the game by one turn
- **Attack**: Perform attack action (placeholder)
- **Cast Spell**: Cast a spell (placeholder)
- **Use Item**: Use an item from inventory (placeholder)

## Testing

Run the test suite to verify the implementation:

```bash
python3 test_pygame_dnd.py
```

This will test:
- Game initialization
- Character creation
- UI element creation
- Basic game mechanics

## Architecture

### Core Components

- **PygameDnDGame**: Main game class managing pygame window and UI
- **UIElement**: Base class for all UI components
- **Button**: Clickable buttons with hover effects
- **Panel**: Text display panels with titles
- **CharacterDisplay**: Character information with health/mana bars

### Game Integration

The pygame version integrates with existing game components:
- `dnd_game.py`: Core game mechanics and character classes
- `narrative_engine.py`: AI-generated narrative content
- `items.py`: Item and inventory system
- `spells.py`: Spell system and spellbook management

### UI System

The UI system is modular and event-driven:
- All UI elements inherit from `UIElement`
- Event handling through `handle_event()` methods
- Callback system for button actions
- Automatic UI updates when game state changes

## Development Status

✅ **Phase 1-4 Complete**: Basic pygame implementation with full UI
🔄 **Phase 5-8 Pending**: Enhanced features and polish

### Completed Features
- Pygame window and event handling
- Complete UI layout with all panels
- Character display with health/mana bars
- Game integration preserving all mechanics
- Button system with hover effects
- Real-time UI updates

### Planned Features
- Character sprites and animations
- Combat visual effects
- Interactive inventory/spell management
- Enhanced narrative display
- Sound effects and music

## Technical Details

- **Resolution**: 1200x800 pixels
- **Frame Rate**: 60 FPS
- **Color Scheme**: D&D-themed browns and golds
- **Font**: Default pygame font
- **Event Handling**: Mouse and keyboard input
- **Architecture**: Event-driven with callback system

## Dependencies

- pygame >= 2.5.0
- All existing AI-DnD dependencies (see requirements.txt)

## File Structure

```
pygame_dnd_game.py     # Main pygame implementation
test_pygame_dnd.py     # Test suite
PYGAME_README.md       # This documentation
```

## Contributing

The pygame implementation follows the same coding standards as the main project:
- Clean, modular code structure
- Comprehensive error handling
- Extensive documentation
- Test coverage for all components

## License

Same license as the main AI-DnD project.
