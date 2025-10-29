# AI-DnD

## Description
**AI-DnD** is an **autonomous, AI-driven D&D campaign simulator** that dynamically generates and evolves its own worlds, histories, and characters. This isn’t just a text-based RPG—it’s a **self-running, self-documenting** AI Dungeon Master that **creates, plays, and archives** full campaigns **without human input**.

### Key Features
- **Autonomous World-Building** – AI characters make decisions, track history, and generate lore in real time.
- **Obsidian Integration** – All campaign events, journals, and lore are automatically saved as Markdown files for easy visualization and review.
- **Sentinel Class** – A monitoring system that ensures narrative and game consistency, acting as a **meta-DM assistant**.
- **Modular Architecture** – Flexible and expandable, allowing for custom modules and mechanics.
- **Local-First AI Execution** – Runs offline for privacy and full control, using AI-powered logic to drive campaigns.

## 🚀 Quick Start (New Features!)

### Try the PixelLab Command Center Dashboard
```bash
# Terminal 1
cd dashboards && python3 -m http.server 8080

# Terminal 2
python3 scripts/pixellab_actions.py --serve

# Open: http://localhost:8080/pixellab_dashboard.html
```

### Run the Automated Test Suite
```bash
curl http://127.0.0.1:8787/test-cases | jq
curl http://127.0.0.1:8787/test/character_generation | jq
```

### Use the Decision Matrix Tool
```bash
python3 task_prioritization.py tasks_config.json
```

See [PixelLab Integration](#pixellab-integration) for complete documentation.

---

## Table of Contents
- [Installation](#installation)
- [Gemini Chat Interface](#gemini-chat-interface) ⭐ NEW
- [Image Generation API](#image-generation-api) ⭐ NEW
- [PixelLab Integration](#pixellab-integration)
  - [⭐ NEW: PixelLab Command Center Dashboard](#-new-pixellab-command-center-dashboard)
  - [🧪 Automated Test Suite](#-automated-test-suite)
  - [🎯 Task Prioritization Tool](#-task-prioritization-tool)
  - [🗺️ Map Generation](#️-map-generation)
- [Obsidian Setup](#obsidian-setup)
- [Usage](#usage)
- [Modules](#modules)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## Installation
To set up **AI-DnD** on your local machine:
```bash
git clone https://github.com/ctavolazzi/AI-DnD.git
cd AI-DnD
pip install -r requirements.txt
```

## Gemini Chat Interface

A modern, standalone chat interface for conversing with Google's Gemini 2.5 Flash model. Perfect for testing AI interactions, prototyping conversations, or just chatting with Gemini!

### Features
- 💬 **Real-time Chat** - Instant responses from Gemini 2.5 Flash
- 🎨 **Modern UI** - Beautiful gradient design with smooth animations
- 💾 **Conversation History** - Context-aware responses that remember the chat
- 🔒 **Secure Storage** - API key stored locally in your browser
- ⌨️ **Keyboard Shortcuts** - Enter to send, Shift+Enter for new lines
- 📱 **Responsive** - Works on desktop and mobile

### Quick Start
```bash
# Option 1: Use the launcher script
./start_gemini_chat.sh

# Option 2: Open directly
open gemini-chat.html
```

### Setup Steps
1. Get your free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Open `gemini-chat.html` in your browser
3. Paste your API key and click "Connect"
4. Start chatting!

### Technical Details
- **Library:** Modern `@google/genai` SDK (GA as of May 2025)
- **Model:** `gemini-2.5-flash` (fast, context-aware responses)
- **Implementation:** Single-file HTML with ES modules
- **No Backend Required:** Runs entirely in the browser

📖 **Full Documentation:** See [GEMINI_CHAT_README.md](GEMINI_CHAT_README.md)

## Image Generation API

AI-DnD includes two powerful image generation systems for creating D&D artwork:

### 🎨 Nano Banana (Photorealistic)
Generate photorealistic scenes, landscapes, and item artwork using Gemini's "Nano Banana" capabilities.

**Two Backend Options:**

1. **FastAPI Backend (Production)** ⭐ - Used by `retro-adventure-game.html`
   - Port 8000
   - SQLite database with scene caching
   - WebP image storage with thumbnails
   - Database migrations with Alembic

2. **Flask Backend (Simple)** - Standalone demos
   - Port 5000
   - In-memory caching only
   - Basic image generation

**Quick Start (FastAPI - Recommended):**
```bash
# Start FastAPI backend
cd backend
./start_server.sh

# Or manually:
uvicorn app.main:app --reload --port 8000

# Open game in browser (served by backend)
open http://localhost:8000
# Or open game file directly
open retro-adventure-game.html
```

**Quick Start (Flask - Simple):**
```bash
# Start Flask backend
python nano_banana_server.py

# Backend runs on port 5000
```

### 🎮 PixelLab (Pixel Art)
Create pixel art characters, sprites, and animations via MCP server integration.

**Features:**
- Text-to-pixel-art generation (Pixflux model)
- Style-based generation (Bitforge model)
- Character rotation and inpainting
- Animation generation

**Quick Start:**
See [PixelLab Integration](#pixellab-integration) below.

### 📚 Complete API Documentation

**[→ View Complete Image Generation API Docs](docs/IMAGE_GENERATION_API.md)**

This comprehensive guide includes:
- ✅ All endpoints and parameters
- ✅ Frontend class methods and events
- ✅ Code examples (basic + advanced)
- ✅ Troubleshooting guide
- ✅ Best practices

**Additional Guides:**
- [Nano Banana Quick Start](NANO_BANANA_QUICKSTART.md)
- [Nano Banana Usage Guide](NANO_BANANA_USAGE.md)
- [PixelLab MCP Setup](PIXELLAB_MCP_SETUP_COMPLETE.md)

## Obsidian Setup
AI-DnD is designed to integrate seamlessly with **Obsidian**, allowing it to generate Markdown-based campaign logs, character journals, and world-building documents in real time.

### Steps to Set Up Obsidian Integration:
1. **Download and Install Obsidian**
   - If you haven't already, download Obsidian from [obsidian.md](https://obsidian.md/) and install it.

2. **Choose or Create an Obsidian Vault**
   - Open Obsidian and create a new vault (or use an existing one) where AI-DnD will store campaign logs.

3. **Configure AI-DnD to Save Logs to Obsidian**
   - In the AI-DnD `config.json` file, set the `obsidian_vault_path` to your chosen Obsidian vault directory.

4. **Run AI-DnD and Verify Logs**
   - Start a new AI-driven campaign and check your Obsidian vault.
   - AI-DnD will generate campaign logs, character journals, and event summaries in **Markdown format**, making them easy to read and edit within Obsidian.

5. **Navigate the Campaign in Obsidian**
   - Open the generated Markdown files in Obsidian to explore the AI-generated world, review past events, and track character development over time.

## PixelLab Integration

AI-DnD now includes **complete PixelLab integration** with both MCP and direct API access, enabling AI-powered pixel art generation for game development.

### ⭐ NEW: PixelLab Command Center Dashboard

**Interactive web-based dashboard for parallel pixel art generation with character rotation!**

```bash
# Terminal 1: Start HTTP server
cd dashboards && python3 -m http.server 8080

# Terminal 2: Start Actions server
python3 scripts/pixellab_actions.py --serve

# Open browser to: http://localhost:8080/pixellab_dashboard.html
```

**Features:**
- 🎨 **Parallel Job Queue** - Run up to 3 character generations simultaneously
- 🔄 **Character Rotation** - Rotate completed characters to all 8 directions
- 📊 **Real-time Monitoring** - Live status updates and comprehensive logging
- 💾 **Job History** - Persistent storage with automatic backups
- 🎮 **Preset Templates** - Quick-start with knight, mage, dragon, and more

See [`dashboards/README.md`](dashboards/README.md) for complete documentation.

### 🧪 Automated Test Suite

**Comprehensive testing framework for PixelLab API endpoints:**

```bash
# List available test suites
curl http://127.0.0.1:8787/test-cases | jq

# Run character generation tests
curl http://127.0.0.1:8787/test/character_generation | jq

# Run character rotation tests
curl http://127.0.0.1:8787/test/character_rotation | jq
```

**Features:**
- 📝 **JSON-based Test Cases** - Easy to write and maintain
- ✅ **Automated Validation** - Response structure, timing, image dimensions
- 📊 **Baseline Comparison** - Compare outputs against known-good results
- 📈 **Test Reports** - JSON and HTML result summaries
- 🔧 **Extensible Framework** - Add new endpoints easily

Test cases are defined in [`pixellab_tests/test_cases/`](pixellab_tests/test_cases/).
See [`pixellab_tests/README.md`](pixellab_tests/README.md) for full documentation.

### 🎯 Task Prioritization Tool

**Decision matrix for evaluating implementation options:**

```bash
# Use default configuration
python3 task_prioritization.py

# Use custom config
python3 task_prioritization.py your_config.json
```

**Evaluates tasks based on:**
- 📈 Short-term impact (1-5 stars)
- 🎯 Long-term impact (1-5 stars)
- ⚡ Energy cost (1-5 hearts)
- 🔋 Available energy budget

Creates JSON config files in this format:
```json
{
  "available_energy": 4,
  "tasks": [
    {
      "name": "Feature Name",
      "short_term": 3,
      "long_term": 4,
      "energy": 2,
      "description": "What this feature does"
    }
  ]
}
```

See [`tasks_config.json`](tasks_config.json) for example configuration.

### 🗺️ Map Generation

NEW! Comprehensive map and tileset generation test suite:

```bash
cd tests/pixellab_map_test
python test_map_generation.py
```

**Features:**
- Top-down terrain tilesets (grass, water, stone, etc.)
- Isometric tiles for strategy games
- 2D platformer tiles and levels
- Complete map composition (8x8 to 16x10 tiles)
- Dungeon generation (walls, doors, treasures)
- Example map builder with RPG overworld, dungeons, platformer levels

See [`tests/pixellab_map_test/README.md`](tests/pixellab_map_test/README.md) for complete documentation.

### Full-Featured Python Client

The `pixellab_integration/` directory provides a complete Python client with:
- Character generation with customizable styles
- Animation creation (walk, run, attack, etc.)
- Multi-directional sprites (4 and 8 directions)
- Rotation and view changes
- Sprite sheet generation
- Game-ready asset workflows

### MCP Integration for Claude Code

AI-DnD also integrates with **PixelLab's Model Context Protocol (MCP)** server, enabling Claude Code to generate game assets through natural language.

### Available Tools

The PixelLab MCP provides the following capabilities:

- **create_character** - Generate pixel art characters with 4 or 8 directional views
  ```python
  create_character(description="fantasy knight", n_directions=8)
  ```

- **animate_character** - Add animations to existing characters (walk, run, idle, etc.)
  ```python
  animate_character(character_id="abc123", animation="walk")
  ```

- **create_topdown_tileset** - Generate Wang tilesets for seamless terrain transitions
  ```python
  create_topdown_tileset(lower="grass", upper="stone path", lower_base_tile_id=0)
  ```

- **create_sidescroller_tileset** - Generate platform tilesets for 2D platformer games
  ```python
  create_sidescroller_tileset(lower="stone brick", transition="moss", base_tile_id=0)
  ```

- **create_isometric_tile** - Create individual isometric tiles
  ```python
  create_isometric_tile(description="medieval tower", size=32)
  ```

### Configuration

The MCP server is configured in `.mcp.json` at the project root. To use PixelLab tools:

1. Get your API key from [pixellab.ai/vibe-coding](https://www.pixellab.ai/vibe-coding)
2. Update the API key in `.mcp.json`
3. Ensure you have Claude Code installed
4. Restart Claude Code to load the MCP server
5. Use natural language to request asset generation (e.g., "Create a pixel art wizard character with 8 directions")

### Use Cases

- Generate character sprites for the game
- Create tile sets for dungeon environments
- Rapidly prototype visual assets during development
- Generate animated sprites for NPCs and monsters

## Usage
To start AI-DnD:

1. Launch the program from the command line or terminal.
2. Select a pre-made campaign or create your own.
3. Observe the AI-driven adventure unfold.
4. Open Obsidian to view real-time campaign logs.

For additional commands and gameplay mechanics, refer to the user documentation.

### Want a quick peek?
If you just want to see the core combat and logging loop in action without
connecting to Ollama, run the lightweight showcase demo:

```bash
cd examples/simple_demo
python demo_app.py --turns 4
```

The demo swaps in a deterministic narrative engine so you can visualize the
Rich HUD and battle flow immediately.

## Modules
### Core Components
- **Character Management** – AI-driven player/NPC attributes, actions, and memory.
- **Combat System** – Simulated D&D battle mechanics with turn-based AI decision-making.
- **Dungeon Master AI** – Generates and narrates the world dynamically.
- **Game State Manager** – Controls the flow of time, events, and interactions.
- **Sentinel System** – Monitors game consistency and flags discrepancies.

### Obsidian Integration
- AI-DnD automatically generates Markdown files to **document campaign history**.
- Players (or the AI itself) can review and expand on these records in Obsidian.

## Configuration
Modify settings in the configuration file to customize:
- Campaign difficulty
- AI randomness & decision weight
- Journal update frequency
- Obsidian vault path

## Contributing
Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a clear description of changes.

## License
This project is licensed under the **MIT License**. See the `LICENSE` file for details.

## Acknowledgments
Special thanks to:
- AI model developers for advancing open-source storytelling.
- The D&D community for inspiring rich, dynamic worlds.
- Open-source contributors helping refine AI-DnD.
