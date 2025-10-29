# 🎉 D&D Narrative Theater - All Systems Operational!

## ✅ Active Servers

### Port 5000 - Nano Banana (Gemini Image Generation)
- **Status:** ✅ Running
- **Purpose:** AI image generation using Gemini 2.5 Flash Image Preview
- **Endpoints:**
  - `GET /health` - Health check
  - `POST /generate` - Generate images
  - `POST /generate-image` - Alternative endpoint
- **Features:** Character portraits, landscape scenes, 16:9 aspect ratio support

### Port 5001 - PixelLab Bridge
- **Status:** ✅ Running
- **Purpose:** Pixel art sprite generation via PixelLab API
- **Endpoints:**
  - `GET /health` - Health check
  - `POST /generate-sprite` - Generate pixel art sprites (64x64)
- **Features:** Fantasy RPG character sprites, pixel art style

### Port 5002 - D&D Narrative Server
- **Status:** ✅ Running
- **Purpose:** Main adventure orchestration and story generation
- **Endpoints:**
  - `GET /health` - Health check
  - `POST /start-adventure` - Start new adventure
  - `POST /generate-scene-image` - Generate scene artwork (uses Nano Banana)
- **Features:** Quest generation, character creation, scene narration

## 🎯 Current Functionality

### Working Features:
1. ✅ **Adventure Generation** - Complete quest and character creation
2. ✅ **Scene Artwork** - Beautiful AI-generated tavern/location scenes
3. ✅ **Character Portraits** - Hero portraits with Gemini
4. ✅ **Pixel Art Sprites** - 64x64 fantasy character sprites (PixelLab)
5. ✅ **Markdown Rendering** - Rich text formatting for quests and scenes
6. ✅ **Multi-Image Gallery** - Three generation methods per scene

## 🔧 Quick Commands

### Check Server Status:
```bash
# All servers
ps aux | grep -E "(nano_banana|dnd_narrative|pixellab_bridge)" | grep -v grep

# Health checks
curl -s http://localhost:5000/health
curl -s http://localhost:5001/health
curl -s http://localhost:5002/health
```

### Stop Servers:
```bash
pkill -f nano_banana_server.py
pkill -f dnd_narrative_server.py
pkill -f pixellab_bridge_server.py
```

### Start Servers:
```bash
python3 nano_banana_server.py > logs/nano_banana.log 2>&1 &
python3 dnd_narrative_server.py > logs/narrative_server.log 2>&1 &
python3 pixellab_bridge_server.py > logs/pixellab_bridge.log 2>&1 &
```

### View Logs:
```bash
tail -f logs/nano_banana.log
tail -f logs/narrative_server.log
tail -f logs/pixellab_bridge.log
```

## 📊 Performance

- **Nano Banana (Gemini):** ~5-20 seconds per image
- **PixelLab Sprites:** ~10 seconds per sprite
- **Adventure Generation:** ~7 seconds

## 🐛 Debugging

### If images fail:
1. Check `GEMINI_API_KEY` in `.env`
2. Check `PIXELLAB_API_KEY` in `.env`
3. Review server logs for errors
4. Verify ports are not in use by other processes

### Console Logging:
Open browser console (F12) to see detailed adventure tracking and debugging info.

## 🎮 Usage

1. Open `dnd-narrative-theater.html` in browser
2. Enter character name (e.g., "Thorin")
3. Select AI model (Gemini recommended)
4. Click "Start Adventure"
5. Click "🎨 Generate Scene Art" for images

## 📝 Notes

- All servers use CORS to allow browser access
- Images are returned as base64-encoded PNG
- Session IDs are stored for continued adventures
- Landscape mode (16:9) provides best scene artwork

---
**Last Updated:** $(date)
**Status:** All systems operational ✅
