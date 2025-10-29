# 🎭 The Narrative Theater 🎲

An interactive D&D storytelling experience where narrative and imagery merge seamlessly. Watch your adventure unfold scene by scene, with AI-generated images bringing key moments to life.

## ✨ Features

- **AI-Powered Narrative**: Stories generated using Ollama LLMs
- **Interactive Pacing**: Control story progression with "Next Scene" button
- **Auto-Image Generation**: Character introductions and combat scenes visualized automatically
- **On-Demand Visualization**: Click "Visualize This!" on any scene
- **Live Character Stats**: Real-time HP tracking with visual feedback
- **Beautiful Medieval UI**: Tavern-themed interface with smooth animations
- **Visual Gallery**: All generated images collected in a sidebar gallery

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** with pip
2. **Ollama** - Install from [ollama.ai](https://ollama.ai)
3. **PixelLab API Key** - Get from [PixelLab](https://pixellab.ai)
4. **Google Gemini API Key** - For Nano Banana image generation

### Installation

```bash
# 1. Set up environment variables
export PIXELLAB_API_KEY=your_pixellab_api_key
export GEMINI_API_KEY=your_gemini_api_key

# 2. Install dependencies
pip install -r narrative_theater_requirements.txt
pip install -r requirements.txt

# 3. Pull Ollama model
ollama pull mistral

# 4. Start all servers
./start_narrative_theater.sh
```

### Open in Browser

Once servers are running, open:
```
file:///path/to/AI-DnD/dnd-narrative-theater.html
```

Or simply double-click `dnd-narrative-theater.html` in your file browser.

## 🎮 How to Use

1. **Start Adventure** - Click to initialize your quest and characters
2. **Read the Scene** - Each scene describes what's happening
3. **Next Scene** - Advance the story when ready
4. **Visualize This!** - Generate an image for any scene
5. **Gallery** - Click images in the gallery to jump to that scene

## 🔧 Architecture

```
┌─────────────────────────────────────────┐
│  dnd-narrative-theater.html (Frontend)  │
│  • Medieval tavern UI                   │
│  • Scene display & management           │
│  • Character stat tracking              │
│  • Image gallery                        │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  dnd_narrative_server.py (Port 5002)    │
│  • Game session management              │
│  • Narrative generation                 │
│  • Scene progression logic              │
│  • Character & combat resolution        │
└──────┬────────────────────┬─────────────┘
       │                    │
       ↓                    ↓
┌─────────────────┐  ┌──────────────────┐
│ PixelLab Bridge │  │  Nano Banana     │
│  (Port 5001)    │  │  (Port 5000)     │
│  • Pixel art    │  │  • Enhanced art  │
│  • Characters   │  │  • Scenes        │
│  • Sprites      │  │  • Backgrounds   │
└─────────────────┘  └──────────────────┘
```

## 📁 Key Files

- `dnd_narrative_server.py` - Backend narrative orchestration
- `dnd-narrative-theater.html` - Frontend UI
- `dnd_game.py` - Game engine (characters, combat, abilities)
- `narrative_engine.py` - AI narrative generation
- `start_narrative_theater.sh` - Convenient server launcher
- `stop_narrative_theater.sh` - Stop all servers

## 🎨 Scene Types

| Type | Description | Auto-Image? |
|------|-------------|-------------|
| **Introduction** | Quest setup & character intros | ✅ Yes |
| **Exploration** | Discovery & investigation | ❌ Manual |
| **Choice** | Player decision moments | ❌ Manual |
| **Combat** | Battle encounters | ✅ Yes |
| **Conclusion** | Adventure finale | ✅ Yes |

## 🐛 Troubleshooting

### Server Won't Start

**Problem**: Port already in use
```bash
./stop_narrative_theater.sh  # Kill old servers
./start_narrative_theater.sh  # Restart
```

**Problem**: Missing dependencies
```bash
pip install -r narrative_theater_requirements.txt
```

### No Images Generating

**Check API Keys:**
```bash
echo $PIXELLAB_API_KEY
echo $GEMINI_API_KEY
```

**Check Server Logs:**
```bash
tail -f logs/pixellab_bridge.log
tail -f logs/nano_banana.log
```

**Restart Image Servers:**
```bash
python3 pixellab_bridge_server.py
python3 nano_banana_server.py
```

### Narrative Generation Failing

**Check Ollama:**
```bash
ollama list  # Verify mistral is installed
ollama run mistral "test"  # Test generation
```

**Check Logs:**
```bash
tail -f logs/narrative_server.log
```

## 📊 API Endpoints

### POST /start-adventure
Initialize a new adventure session
```json
{
  "session_id": "optional_custom_id",
  "model": "mistral"
}
```

### POST /next-scene
Generate the next scene
```json
{
  "session_id": "session_xxx"
}
```

### POST /generate-scene-image
Create an image for a scene
```json
{
  "session_id": "session_xxx",
  "scene_id": 0,
  "scene_description": "...",
  "scene_type": "combat"
}
```

### GET /game-state
Get current game state
```
?session_id=session_xxx
```

## 🔮 Future Enhancements

- [ ] Multiplayer support
- [ ] Voice narration (TTS)
- [ ] Background music generation
- [ ] Map visualization
- [ ] Inventory UI with item images
- [ ] Save/load adventures
- [ ] Character customization before starting
- [ ] Choice branching narratives
- [ ] Combat animations
- [ ] WebSocket for real-time updates

## 📝 Development

### Running Tests
```bash
# Test narrative generation
python3 -c "from narrative_engine import NarrativeEngine; e = NarrativeEngine(); print(e.generate_quest())"

# Test game engine
python3 -c "from dnd_game import DnDGame; g = DnDGame(); print(g.players[0].name)"

# Test server health
curl http://localhost:5002/health
```

### Logs Location
- `logs/narrative_server.log` - Narrative generation & game logic
- `logs/pixellab_bridge.log` - Pixel art generation
- `logs/nano_banana.log` - Enhanced image generation

## 🎯 Credits

Built with:
- [Ollama](https://ollama.ai) - Local LLM inference
- [PixelLab](https://pixellab.ai) - Pixel art generation
- [Google Gemini](https://ai.google.dev) - Image enhancement
- [Flask](https://flask.palletsprojects.com/) - Backend server
- Love for D&D ❤️

## 📜 License

Part of the AI-DnD project. See main repository for license details.

---

**🎭 The stage is set. Your adventure awaits! 🎲**

