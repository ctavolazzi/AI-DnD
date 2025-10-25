# Nano Banana Quick Start 🍌

## What is This?
Your retro adventure game now generates AI-powered images using Gemini's image generation! See photorealistic D&D scenes, character portraits, and item artwork as you play.

## Quick Start (3 Steps)

### 1. Start the Backend Server
```bash
cd /Users/ctavolazzi/Code/AI-DnD
python3 nano_banana_server.py
```

You should see:
```
🍌 Nano Banana Image Generation Server
✓ API Key configured
✓ Running on http://localhost:5000
```

### 2. Open the Game
```bash
open retro-adventure-game.html
```

Or double-click `retro-adventure-game.html` in Finder.

### 3. Watch the Magic!
The game will automatically:
- Generate the Emberpeak village entrance scene
- Display it in the new "SCENE VIEWER 🍌" panel
- Show you a photorealistic D&D landscape!

## What You'll See

```
┌─────────────────────────────────────────┐
│ [ SCENE VIEWER 🍌 ]                    │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │     [AI-Generated Image Here]       │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Features You Can Use

### In Browser Console (F12):
```javascript
// Generate a new scene
await nanoBanana.generateSceneImage(
    'a dark mine tunnel with glowing crystals',
    { style: 'fantasy_art', aspectRatio: '16:9' }
);

// Generate a character portrait
await nanoBanana.generateCharacterPortrait({
    name: 'Thorin',
    class: 'Dwarf Fighter',
    description: 'grizzled warrior'
});

// Generate item artwork
await nanoBanana.generateItemImage('Glowing Sword');
```

## Troubleshooting

### "Server not available" message?
1. Check server is running: `curl http://localhost:5000/health`
2. Restart server: `python3 nano_banana_server.py`

### Port 5000 already in use?
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Then restart server
python3 nano_banana_server.py
```

### Images not generating?
1. Check `.env` file has `GEMINI_API_KEY=your_key`
2. Verify API key is valid at https://ai.google.dev/
3. Check browser console (F12) for errors

## Next Steps

See `NANO_BANANA_USAGE.md` for:
- Complete API reference
- Advanced usage examples
- All available features
- Customization options

## Files Created
- `nano_banana_server.py` - Backend API server
- `NANO_BANANA_USAGE.md` - Full documentation
- `NANO_BANANA_QUICKSTART.md` - This file
- Work effort: `_work_efforts_/10-19_development/10_core/10.06_nano_banana_image_generation_integration.md`

## How It Works

```
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   Game (HTML)    │──────▶│  Flask Server    │──────▶│   Gemini API     │
│                  │       │  (Port 5000)     │       │                  │
│  - UI Display    │       │  - API Key       │       │  - Generate      │
│  - User Input    │       │  - Rate Limit    │       │  - Return Image  │
│  - Caching       │       │  - Error Handle  │       │                  │
└──────────────────┘◀──────└──────────────────┘◀──────└──────────────────┘
```

## Rate Limits
- 10 images per minute
- Images are cached (no redundant API calls)
- Clear cache: `nanoBanana.clearCache()`

## Cost
Gemini image generation pricing: https://ai.google.dev/pricing

Images use ~1290 tokens each.

Enjoy your AI-enhanced D&D adventure! 🎮⚔️🍌

