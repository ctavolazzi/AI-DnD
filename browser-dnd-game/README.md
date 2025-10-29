# Browser D&D Game - The Emberpeak Expedition

A modern browser-based D&D adventure game built with vanilla JavaScript, featuring a comprehensive save system and retro RPG aesthetics.

## 🎮 Features

### Start Screen
- **New Game**: Create a character and start your adventure
- **Load Game**: Resume from saved games with full state restoration
- **Character Creation**: Choose name, class, and race
- **Save Management**: View, load, and delete save files

### Save System
- **Auto-save**: Automatic saving every 30 seconds during gameplay
- **Manual Save**: Save at any time with custom names
- **Local Storage**: All saves stored in browser's localStorage
- **State Management**: Complete game state preservation
- **Import/Export**: Save data can be exported and imported

### Game Engine
- **Event-Driven Architecture**: Pub/sub system for clean component communication
- **State Management**: Centralized state with history tracking
- **Modular Design**: Separate engine, systems, UI, and data layers
- **Debug Mode**: Comprehensive logging and debugging tools

## 🚀 Quick Start

1. **Open the game**: Simply open `index.html` in your web browser
2. **Create character**: Click "New Game" and fill out character details
3. **Start playing**: Click "Start Adventure" to begin your journey
4. **Save progress**: Game auto-saves every 30 seconds, or use Ctrl+S for quick save

## 📁 Project Structure

```
browser-dnd-game/
├── index.html              # Main HTML file
├── css/
│   ├── main.css            # Core styles and theme
│   └── start-screen.css    # Start screen specific styles
├── js/
│   ├── engine/             # Game engine components
│   │   ├── EventBus.js     # Pub/sub event system
│   │   ├── StateManager.js # Centralized state management
│   │   ├── SaveManager.js  # Save/load functionality
│   │   └── GameEngine.js   # Main game coordinator
│   ├── ui/                 # User interface components
│   │   └── StartScreen.js  # Start screen logic
│   └── main.js             # Application entry point
├── assets/                 # Game assets (images, sounds)
├── saves/                  # Save files directory
└── README.md              # This file
```

## 🎯 Architecture

### Event System
The game uses a centralized event bus for component communication:
```javascript
// Subscribe to events
eventBus.on('gameSaved', (data) => {
    console.log('Game saved:', data.saveName);
});

// Emit events
eventBus.emit('startNewGame');
```

### State Management
All game state is managed centrally with change tracking:
```javascript
// Update state
stateManager.setState('player.name', 'Aragorn');
stateManager.setState('player.hp', 100);

// Get state
const playerName = stateManager.getStateValue('player.name');
```

### Save System
Saves are stored as JSON in localStorage with full validation:
```javascript
// Save game
saveManager.saveGame('my-save');

// Load game
saveManager.loadGame('my-save');

// Get all saves
const saves = saveManager.getAllSaves();
```

## 🎨 Theming

The game uses CSS custom properties for easy theming:
- **Colors**: Retro RPG palette with browns, golds, and parchment
- **Typography**: Press Start 2P for UI, Cinzel for titles
- **Animations**: Smooth transitions and hover effects
- **Responsive**: Works on desktop and mobile devices

## ⌨️ Keyboard Shortcuts

- **F1**: Show help information
- **Escape**: Return to main menu
- **Ctrl+S**: Quick save (in game)
- **Ctrl+L**: Quick load (from menu)

## 🔧 Development

### Debug Mode
Enable debug mode by opening the browser console and running:
```javascript
gameEngine.setDebug(true);
startScreen.setDebug(true);
```

### Adding New Features
1. Create new components in appropriate directories
2. Use the event bus for communication
3. Update state through the state manager
4. Follow the existing code patterns

### Save Data Format
Save files are JSON objects with this structure:
```json
{
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2025-10-28T19:40:26.000Z",
    "saveName": "my-save",
    "currentTurn": 5
  },
  "state": {
    "player": { "name": "Aragorn", "hp": 100, ... },
    "world": { "currentLocation": "start", ... },
    "quests": { "active": [], "completed": [] }
  }
}
```

## 🐛 Troubleshooting

### Game Won't Load
- Check browser console for errors
- Ensure JavaScript is enabled
- Try refreshing the page

### Save Issues
- Check if localStorage is available
- Clear browser data if saves are corrupted
- Use browser dev tools to inspect localStorage

### Performance Issues
- Disable debug mode in production
- Check for memory leaks in browser dev tools
- Clear old save files if storage is full

## 📝 License

This project is part of the AI-DnD game development series. See the main project for licensing information.

## 🤝 Contributing

This is a learning project showcasing modern JavaScript game development patterns. Feel free to use as a reference or starting point for your own projects.

---

**Built with ❤️ and AI assistance**
