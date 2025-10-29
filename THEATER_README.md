# 🎭 D&D Narrative Theater - Complete Guide 🎲

Welcome to the **AI-Powered D&D Adventure System**! This system uses advanced AI to generate complete D&D adventures with beautiful artwork, compelling stories, and dynamic characters.

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Make scripts executable
chmod +x start_theater.sh stop_theater.sh

# 2. Start everything
./start_theater.sh

# 3. Play in your browser (opens automatically)
# OR open: dnd-narrative-theater.html

# 4. When done
./stop_theater.sh
```

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [First-Time Setup](#first-time-setup)
3. [Running the Theater](#running-the-theater)
4. [How to Use](#how-to-use)
5. [Troubleshooting](#troubleshooting)
6. [Architecture](#architecture)
7. [Advanced Usage](#advanced-usage)

---

## ✅ Prerequisites

### Required:
- **Python 3.10+** installed
- **Gemini API Key** (for AI image generation)
  - Get one at: https://aistudio.google.com/app/apikey
- **Modern web browser** (Chrome, Firefox, Safari, Edge)

### Optional:
- **PixelLab API Key** (for pixel art sprites)
  - Get one at: https://pixellab.ai

### Python Packages:
All required packages are listed in the server files. If you get import errors, install:

```bash
pip3 install flask flask-cors python-dotenv pillow google-genai pixellab
```

---

## 🔧 First-Time Setup

### Step 1: Create Environment File

Create a file named `.env` in the project directory:

```bash
# Create .env file
cat > .env << 'EOF'
# Required - Get from https://aistudio.google.com/app/apikey
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Get from https://pixellab.ai
PIXELLAB_API_KEY=your_pixellab_api_key_here
EOF
```

**Edit the file** and replace `your_gemini_api_key_here` with your actual API key.

### Step 2: Make Scripts Executable

```bash
chmod +x start_theater.sh
chmod +x stop_theater.sh
```

### Step 3: Test Your Setup

```bash
# Test that Python and packages are available
python3 -c "import flask, google.genai; print('✅ Setup looks good!')"
```

---

## 🎮 Running the Theater

### Start Everything (Easy Mode)

```bash
./start_theater.sh
```

This script will:
1. ✅ Check your `.env` configuration
2. ✅ Check if servers are already running
3. ✅ Start all three required servers
4. ✅ Wait for them to be ready
5. ✅ Open the theater in your browser
6. ✅ Show you the status

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║       🎭  D&D NARRATIVE THEATER - STARTUP SCRIPT  🎲         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

🔍 Checking environment configuration...
✅ Environment configuration OK

🚀 Starting servers...

[1/3] Starting Nano Banana Server (Gemini Image Generation)...
✅ Nano Banana started (PID: 12345)
✅ Nano Banana Server is ready!

[2/3] Starting PixelLab Bridge Server (Pixel Art Sprites)...
✅ PixelLab Bridge started (PID: 12346)
✅ PixelLab Bridge Server is ready!

[3/3] Starting D&D Narrative Server (Adventure Orchestration)...
✅ Narrative Server started (PID: 12347)
✅ D&D Narrative Server is ready!

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║          🎉  ALL SYSTEMS OPERATIONAL!  🎉                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Stop Everything

```bash
./stop_theater.sh
```

### Manual Start (Advanced)

If you prefer to start servers manually:

```bash
# Terminal 1 - Nano Banana (Port 5000)
python3 nano_banana_server.py

# Terminal 2 - PixelLab Bridge (Port 5001)
python3 pixellab_bridge_server.py

# Terminal 3 - Narrative Server (Port 5002)
python3 dnd_narrative_server.py
```

---

## 🎯 How to Use

### 1. Open the Theater

After running `./start_theater.sh`, your browser should open automatically to:
```
file:///path/to/AI-DnD/dnd-narrative-theater.html
```

Or open it manually by double-clicking `dnd-narrative-theater.html`

### 2. Start an Adventure

![Theater Interface](docs/theater-interface.png)

1. **Enter Character Name**: Type your hero's name (e.g., "Thorin", "Aria")
2. **Select AI Model**: Choose "Gemini" (recommended)
3. **Click "Start Adventure"**

Wait ~7 seconds while the AI generates:
- ✨ A complete quest with objectives
- 👥 Two unique party members
- 📖 An immersive opening scene

### 3. Generate Scene Artwork

Click **"🎨 Generate Scene Art"** button to create three types of images:

1. **🎮 PixelLab Sprite** - 64x64 pixel art (retro style)
2. **🎨 Nano Banana Landscape** - 16:9 AI artwork (main image)
3. **✨ Enhanced Pipeline** - Combined sprite + landscape

**Generation takes 10-30 seconds** - watch the console for progress!

### 4. Explore Your Adventure

- Read the quest objectives
- View your party members' stats
- Enjoy the AI-generated narrative
- Generate multiple scenes for different locations

---

## 🐛 Troubleshooting

### Problem: "ERROR: .env file not found!"

**Solution:**
```bash
# Create the .env file
cat > .env << 'EOF'
GEMINI_API_KEY=your_actual_key_here
PIXELLAB_API_KEY=your_actual_key_here
EOF
```

### Problem: "Port 5000/5001/5002 already in use"

**Solution:**
```bash
# Option 1: Let the script handle it
./start_theater.sh
# Choose option 1 to restart servers

# Option 2: Manually stop processes
./stop_theater.sh
```

### Problem: "Image generation failed (500 error)"

**Possible causes:**
1. **Missing API key** - Check `.env` file
2. **Invalid API key** - Verify your Gemini API key
3. **Server not running** - Run `./start_theater.sh`

**Check server status:**
```bash
curl http://localhost:5000/health  # Nano Banana
curl http://localhost:5001/health  # PixelLab
curl http://localhost:5002/health  # Narrative Server
```

### Problem: "Connection refused" errors

**Solution:**
```bash
# Check if servers are running
ps aux | grep -E "(nano_banana|pixellab|dnd_narrative)" | grep -v grep

# If not running, start them
./start_theater.sh
```

### Problem: Images not showing in browser

**Check:**
1. Open browser console (F12) - look for errors
2. Verify servers are running: `./start_theater.sh`
3. Check network tab for failed requests
4. Make sure CORS is enabled (should be automatic)

### View Server Logs

```bash
# Follow logs in real-time
tail -f logs/nano_banana.log
tail -f logs/pixellab_bridge.log
tail -f logs/narrative_server.log

# View recent errors
grep -i error logs/*.log
```

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR BROWSER                             │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │      dnd-narrative-theater.html                      │   │
│  │  (Frontend / User Interface)                         │   │
│  └────────────┬─────────────┬──────────────┬───────────┘   │
└───────────────┼─────────────┼──────────────┼───────────────┘
                │             │              │
                │             │              │
        ┌───────▼──────┐ ┌───▼─────┐ ┌─────▼────────┐
        │   Port 5000  │ │Port 5001│ │  Port 5002   │
        │              │ │         │ │              │
        │ Nano Banana  │ │PixelLab │ │  Narrative   │
        │   Server     │ │ Bridge  │ │   Server     │
        │              │ │         │ │              │
        │  (Gemini     │ │(Pixel   │ │ (Adventure   │
        │   Images)    │ │ Art)    │ │  Generator)  │
        └──────────────┘ └─────────┘ └──────────────┘
                │              │            │
                │              │            │
                ▼              ▼            ▼
        ┌──────────────────────────────────────┐
        │      Google Gemini API               │
        │      PixelLab API                    │
        └──────────────────────────────────────┘
```

### Components

#### 1. **Frontend (dnd-narrative-theater.html)**
- Single-page web application
- No build process needed
- Real-time console logging
- Markdown rendering with Marked.js

#### 2. **Nano Banana Server (Port 5000)**
- Gemini 2.5 Flash Image Preview
- Generates character portraits and scenes
- Supports 1:1 and 16:9 aspect ratios
- ~5-20 seconds per image

#### 3. **PixelLab Bridge (Port 5001)**
- PixelLab API integration
- 64x64 pixel art sprites
- Fantasy RPG character style
- ~10 seconds per sprite

#### 4. **Narrative Server (Port 5002)**
- Main orchestration server
- Generates quests and characters
- Manages adventure sessions
- Coordinates image generation

---

## 🔥 Advanced Usage

### Custom Quest Themes

Edit `dnd_narrative_server.py` to customize quest types:

```python
# Line ~150 (approximate)
QUEST_THEMES = [
    "underwater adventure",
    "haunted castle",
    "dragon's lair",
    "your_custom_theme_here"  # Add your own!
]
```

### Adjust Image Generation Settings

Edit `nano_banana_server.py`:

```python
# Line ~60 (approximate)
DEFAULT_ASPECT_RATIO = "16:9"  # Change to "1:1" for square images
DEFAULT_MODALITIES = ["Text", "Image"]  # Adjust output types
```

### Monitor Performance

```bash
# Watch server activity
watch -n 1 'ps aux | grep -E "(nano_banana|pixellab|dnd_narrative)" | grep -v grep'

# Check ports
lsof -i :5000 -i :5001 -i :5002

# Monitor logs with timestamps
tail -f logs/*.log | awk '{print strftime("[%H:%M:%S]"), $0}'
```

### Development Mode

For development with hot reload:

```bash
# Install watchdog
pip3 install watchdog

# Run with auto-restart (if you have nodemon or similar)
nodemon --exec python3 nano_banana_server.py
```

---

## 📊 Performance & Costs

### Typical Generation Times
- **Adventure Start**: ~7 seconds
- **Gemini Scene Image**: 5-20 seconds
- **PixelLab Sprite**: 10 seconds
- **Character Portraits**: 5-10 seconds each

### API Costs (Approximate)
- **Gemini API**: Free tier available, then $0.075 per 1M tokens
- **PixelLab API**: Pricing varies, check their website

### Optimization Tips
1. Reuse sessions instead of creating new adventures
2. Cache generated images locally
3. Reduce image sizes if needed
4. Use rate limiting for production

---

## 🎨 Features Showcase

### ✅ Working Features

1. **🎭 Adventure Generation**
   - Dynamic quest creation
   - Randomized objectives
   - Location-based themes

2. **👥 Character Creation**
   - Two unique party members
   - Balanced stats and abilities
   - Class-based skills

3. **🖼️ Multi-Format Artwork**
   - Pixel art sprites (64x64)
   - Landscape scenes (16:9)
   - Portrait mode (1:1)

4. **📖 Rich Narratives**
   - Markdown formatting
   - Immersive descriptions
   - Quest objectives and lore

5. **🎮 Interactive UI**
   - Real-time generation feedback
   - Image galleries
   - Session management

---

## 🆘 Getting Help

### Check These First
1. ✅ Is `.env` configured with valid API keys?
2. ✅ Are all three servers running?
3. ✅ Check browser console (F12) for errors
4. ✅ Review server logs in `logs/` directory

### Common Commands

```bash
# Check environment
cat .env

# Check server status
curl http://localhost:5002/health | jq

# Test image generation
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}' | jq '.success'

# View all processes
ps aux | grep python

# Kill everything
./stop_theater.sh
```

### Still Having Issues?

Check `logs/` directory for detailed error messages:
```bash
cat logs/nano_banana.log
cat logs/pixellab_bridge.log
cat logs/narrative_server.log
```

---

## 🎉 Enjoy Your Adventures!

You're all set! Fire up the theater and embark on AI-generated D&D adventures.

**Remember:**
- Start servers: `./start_theater.sh`
- Stop servers: `./stop_theater.sh`
- Check status: `curl http://localhost:5002/health`

**May your dice roll high!** 🎲✨

---

*Last updated: 2025-10-29*
*Version: 2.0.0 (Simple Edition)*

