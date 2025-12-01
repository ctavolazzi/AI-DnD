# AI-DnD

## Description
**AI-DnD** is an **autonomous, AI-driven D&D campaign simulator** that dynamically generates and evolves its own worlds, histories, and characters. This isn’t just a text-based RPG—it’s a **self-running, self-documenting** AI Dungeon Master that **creates, plays, and archives** full campaigns **without human input**.

### Key Features
- **Autonomous World-Building** – AI characters make decisions, track history, and generate lore in real time.
- **Integrated Generative AI** – Features standalone interfaces for chatting with Google's Gemini models and generating professional game assets.
- **Obsidian Integration** – All campaign events, journals, and lore are automatically saved as Markdown files for easy visualization and review.
- **Sentinel Class** – A monitoring system that ensures narrative and game consistency, acting as a **meta-DM assistant**.
- **Modular Architecture** – Flexible and expandable, allowing for custom modules and mechanics.

---

## 🚀 Quick Start (New Features!)

### 💬 Try the Standalone Gemini Chat
Interact directly with the Gemini 2.5 Flash model in a modern, local web interface.
```bash
# Make script executable first: chmod +x start_gemini_chat.sh
./start_gemini_chat.sh
```

### 🎨 Start the Nano Banana Image Server (FastAPI)

Power photorealistic asset generation for your game frontend.

```bash
cd backend
./start_server.sh
# Then open http://localhost:8000/retro-adventure-game.html
```

### 🕹️ Try the PixelLab Command Center Dashboard

Monitor parallel pixel art generation jobs.

```bash
# Terminal 1: Start HTTP server
cd dashboards && python3 -m http.server 8080

# Terminal 2: Start Actions server
python3 scripts/pixellab_actions.py --serve

# Open: http://localhost:8080/pixellab_dashboard.html
```

-----

## Table of Contents

  - [Installation](https://www.google.com/search?q=%23installation)
  - [Gemini Chat Interface](https://www.google.com/search?q=%23gemini-chat-interface) ⭐ NEW
  - [Image Generation API](https://www.google.com/search?q=%23image-generation-api) ⭐ NEW
  - [PixelLab Integration](https://www.google.com/search?q=%23pixellab-integration)
      - [⭐ NEW: PixelLab Command Center Dashboard](https://www.google.com/search?q=%23-new-pixellab-command-center-dashboard)
      - [🧪 Automated Test Suite](https://www.google.com/search?q=%23-automated-test-suite)
      - [🎯 Task Prioritization Tool](https://www.google.com/search?q=%23-task-prioritization-tool)
      - [🗺️ Map Generation](https://www.google.com/search?q=%23%EF%B8%8F-map-generation)
  - [Obsidian Setup](https://www.google.com/search?q=%23obsidian-setup)
  - [Usage](https://www.google.com/search?q=%23usage)
  - [Modules](https://www.google.com/search?q=%23modules)
  - [Configuration](https://www.google.com/search?q=%23configuration)
  - [Contributing](https://www.google.com/search?q=%23contributing)
  - [License](https://www.google.com/search?q=%23license)

## Installation

To set up **AI-DnD** on your local machine:

```bash
git clone [https://github.com/ctavolazzi/AI-DnD.git](https://github.com/ctavolazzi/AI-DnD.git)
cd AI-DnD
pip install -r requirements.txt
```

-----

## Gemini Chat Interface

A modern, standalone chat interface for conversing with Google's Gemini 2.5 Flash model. This tool is perfect for testing AI interactions, prototyping NPC dialogue, or just chatting with the model outside of the main game loop.

### Features

  - 💬 **Real-time Chat** - Instant responses from Gemini 2.5 Flash.
  - 🎨 **Modern UI** - Beautiful gradient design with smooth animations.
  - 💾 **Context-Aware** - Remembers conversation history for coherent replies.
  - 🔒 **Secure Storage** - API key stored locally in your browser.
  - 📱 **Responsive** - Works flawlessly on desktop and mobile.

### Quick Start

1.  **Get an API Key:** Get your free key from [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  **Launch:** Run `./start_gemini_chat.sh` OR directly open `gemini-chat.html` in your browser.
3.  **Connect:** Paste your API key into the settings panel and connect.

📖 **Full Documentation:** See [GEMINI_CHAT_README.md](https://www.google.com/search?q=GEMINI_CHAT_README.md) for technical details.

-----

## Image Generation API

AI-DnD includes a powerful, dual-engine image generation system designed for creating professional D&D artwork on the fly.

### 🎨 Engine 1: Nano Banana (Photorealistic)

Utilizes Google's Gemini model to generate stunning, photorealistic scenes, landscapes, and item artwork. It powers the visuals in the `retro-adventure-game.html` frontend.

**Recommended Backend (FastAPI):**
The robust, production-ready server featuring SQLite caching, WebP image optimization, and database migrations.

```bash
# Start the FastAPI backend
cd backend
./start_server.sh

# Access the game at http://localhost:8000/retro-adventure-game.html
# Access API docs at http://localhost:8000/docs
```

*(A simpler Flask backend is also available for standalone demos in `nano_banana_server.py`)*

### 👾 Engine 2: PixelLab (Pixel Art)

Specializes in generating retro pixel art characters, sprites, animations, and tilesets via MCP server integration.

*See the detailed [PixelLab Integration](https://www.google.com/search?q=%23pixellab-integration) section below for usage capabilities.*

### 📚 Complete API Documentation

**[→ View Complete Image Generation API Docs](https://www.google.com/search?q=docs/IMAGE_GENERATION_API.md)**

This comprehensive guide includes endpoint references, frontend usage examples, troubleshooting steps, and best practices for both engines.

-----

## Obsidian Setup

AI-DnD is designed to integrate seamlessly with **Obsidian**, allowing it to generate Markdown-based campaign logs, character journals, and world-building documents in real time.

1.  **Install Obsidian:** Download from [obsidian.md](https://obsidian.md/).
2.  **Create Vault:** Create a new vault where AI-DnD will store campaign logs.
3.  **Configure Path:** In the AI-DnD `config.json` file, set the `obsidian_vault_path` to your chosen Obsidian vault directory.
4.  **Run & Observe:** Start a campaign. AI-DnD will generate auto-linked Markdown files in your vault as the game progresses.

-----

## PixelLab Integration

AI-DnD includes **complete PixelLab integration** with both MCP and direct API access, enabling AI-powered pixel art generation for game development.

### ⭐ NEW: PixelLab Command Center Dashboard

**Interactive web-based dashboard for parallel pixel art generation with character rotation!**

*Instructions located in the Quick Start section above.*

**Features:**

  - 🎨 **Parallel Job Queue** - Run up to 3 character generations simultaneously
  - 🔄 **Character Rotation** - Rotate completed characters to all 8 directions
  - 📊 **Real-time Monitoring** - Live status updates and comprehensive logging
  - 💾 **Job History** - Persistent storage with automatic backups

See [`dashboards/README.md`](https://www.google.com/search?q=dashboards/README.md) for complete documentation.

### 🧪 Automated Test Suite

**Comprehensive testing framework for PixelLab API endpoints:**

```bash
# Run character generation tests
curl http://127.0.0.1:8787/test/character_generation | jq
```

See [`pixellab_tests/README.md`](https://www.google.com/search?q=pixellab_tests/README.md) for full documentation.

### 🎯 Task Prioritization Tool

**Decision matrix for evaluating implementation options based on impact vs. energy cost.**

See [`tasks_config.json`](https://www.google.com/search?q=tasks_config.json) for example configuration.

### 🗺️ Map Generation

Comprehensive test suite for generating top-down, isometric, and platformer tilesets and complete dungeon maps.

See [`tests/pixellab_map_test/README.md`](https://www.google.com/search?q=tests/pixellab_map_test/README.md) for documentation.

### MCP Integration for Claude Code

AI-DnD integrates with **PixelLab's Model Context Protocol (MCP)** server, enabling Claude Code to generate pixel art assets directly through natural language.

#### 🔧 Setup MCP Server

Add the PixelLab MCP server to your Claude Code configuration:

```bash
claude mcp add pixellab https://api.pixellab.ai/mcp -t http -H "Authorization: Bearer YOUR_API_KEY"
```

Replace `YOUR_API_KEY` with your actual PixelLab API key from [https://www.pixellab.ai](https://www.pixellab.ai)

#### 📋 Configuration

The MCP server configuration is stored in `.mcp.json`:

```json
{
  "mcpServers": {
    "pixellab": {
      "type": "http",
      "url": "https://api.pixellab.ai/mcp",
      "headers": {
        "Authorization": "Bearer ${PIXELLAB_API_KEY}"
      }
    }
  }
}
```

For local development, set `PIXELLAB_API_KEY` in your `.env` file.

#### ✨ Capabilities

With MCP integration, you can ask Claude Code to:
- "Create a pixel art wizard character facing 8 directions"
- "Generate a walking animation for this character"
- "Rotate this sprite to face north"
- "Create an isometric tileset for a dungeon"

#### 🐍 Python Client

For programmatic access, use the PixelLabClient:

```python
from pixellab_integration.pixellab_client import PixelLabClient

client = PixelLabClient(api_key="your-api-key")

# Generate character
character = client.generate_character(
    description="cyberpunk hacker",
    width=64,
    height=64,
    no_background=True
)

# Create 8-directional sprite
sprites = client.batch_generate_directions(
    description="cyberpunk hacker",
    directions=['north', 'south', 'east', 'west']
)

# Animate character
frames = client.animate_character_text(
    reference_image=character,
    description="cyberpunk hacker",
    action="walk",
    n_frames=4
)
```

See `pixellab_integration/pixellab_client.py` for complete API documentation.

#### 🎮 Game Asset Generator

Automate creation of complete character sprite sets with the Game Asset Generator utility:

```bash
# Generate a player character with 8-directional sprites + animations
python utils/game_asset_generator.py --character "elven ranger" --animations walk,idle,attack

# Generate an NPC
python utils/game_asset_generator.py --npc "goblin warrior" --size 48

# Batch generate multiple characters from JSON file
python utils/game_asset_generator.py --batch utils/example_character_batch.json
```

**Features:**
- 8-directional sprites (N, NE, E, SE, S, SW, W, NW)
- Walking and action animations
- Organized sprite sheets
- Metadata files for easy integration
- Batch processing support

Output is saved to `assets/generated/` with organized directories per character.

-----

## Usage

To start the main AI-DnD simulation loop:

1.  Launch the main program script (e.g., `python main.py`).
2.  Select a pre-made campaign scenario or create a new one.
3.  Observe the AI-driven adventure unfold in your terminal.
4.  Open your linked Obsidian vault to view real-time, formatted campaign logs.

-----

## Modules

### Core Components

  - **Character Management** – AI-driven player/NPC attributes, actions, and memory.
  - **Combat System** – Simulated D&D battle mechanics with turn-based AI decision-making.
  - **Dungeon Master AI** – Generates and narrates the world dynamically.
  - **Game State Manager** – Controls the flow of time, events, and interactions.
  - **Sentinel System** – Monitors game consistency and flags discrepancies.

## Configuration

Modify settings in the `config.json` file to customize:

  - Campaign difficulty and AI randomness.
  - Journal update frequency.
  - Obsidian vault path.
  - API keys for Gemini and PixelLab services.

## Contributing

Contributions are welcome! To contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Submit a pull request with a clear description of changes.

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

