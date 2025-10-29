# Sprite Enhancer - PixelLab + Nano Banana 🎨🍌

A simple web application that generates pixel art sprites with PixelLab and enhances them to photorealistic versions using Nano Banana (Gemini).

## Workflow

1. **Generate Sprite** - Enter a description and generate pixel art using PixelLab
2. **Enhance** - Click "Enhance" to create a detailed/photorealistic version with Gemini
3. **Compare** - See pixel art vs enhanced version side-by-side

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install flask flask-cors pillow pixellab python-dotenv google-generativeai

# Set API keys
export PIXELLAB_API_KEY="your-pixellab-api-key"
export GEMINI_API_KEY="your-gemini-api-key"
```

### Start Servers

You need to run TWO servers:

#### Terminal 1: PixelLab Bridge Server (Port 5001)
```bash
python3 pixellab_bridge_server.py
```

#### Terminal 2: Nano Banana Server (Port 5000)
```bash
python3 nano_banana_server.py
```

### Open the App

```bash
open sprite-enhancer.html
```

Or navigate to `sprite-enhancer.html` in your browser.

## Features

### Sprite Generation (PixelLab)
- **Text-to-pixel-art** - Generate sprites from descriptions
- **Multiple sizes** - 64x64, 128x128, 256x256
- **Transparent backgrounds** - Perfect for sprites
- **Customizable** - Outline, shading, detail levels

### Enhancement (Nano Banana)
- **Style options** - Photorealistic, Fantasy Art, Comic
- **Additional details** - Add lighting, setting, atmosphere
- **High quality** - Gemini 2.5 Flash Image generation
- **Fast** - ~2-3 seconds per enhancement

## API Keys

### PixelLab API Key
1. Visit [PixelLab](https://www.pixellab.ai)
2. Sign up and get your API key
3. Set environment variable: `export PIXELLAB_API_KEY="your-key"`

### Gemini API Key
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Get your API key
3. Set environment variable: `export GEMINI_API_KEY="your-key"`

## Usage Examples

### Example 1: Fantasy Knight
1. **Description:** "fantasy knight with sword and shield"
2. **Size:** 64x64
3. **Generate** → Pixel art sprite
4. **Enhance Style:** Photorealistic
5. **Additional Details:** "cinematic lighting, epic fantasy setting"
6. **Enhance** → Detailed knight image

### Example 2: Space Explorer
1. **Description:** "astronaut with futuristic space suit"
2. **Size:** 128x128
3. **Generate** → Pixel art astronaut
4. **Enhance Style:** Fantasy Art
5. **Additional Details:** "dramatic space background, stars"
6. **Enhance** → Detailed space explorer

### Example 3: Pixel Dragon
1. **Description:** "dragon breathing fire"
2. **Size:** 256x256
3. **Generate** → Pixel art dragon
4. **Enhance Style:** Comic
5. **Additional Details:** "comic book style, bold colors"
6. **Enhance** → Comic-style dragon

## File Structure

```
sprite-enhancer.html          # Main web interface
pixellab_bridge_server.py     # PixelLab API bridge (port 5001)
nano_banana_server.py         # Gemini enhancement server (port 5000)
SPRITE_ENHANCER_README.md     # This file
```

## Troubleshooting

### "Cannot connect to PixelLab server"
- Check that `pixellab_bridge_server.py` is running on port 5001
- Verify `PIXELLAB_API_KEY` is set
- Check terminal output for errors

### "Cannot connect to Nano Banana server"
- Check that `nano_banana_server.py` is running on port 5000
- Verify `GEMINI_API_KEY` is set
- Check terminal output for errors

### "API key not configured"
- Make sure environment variables are set in the same terminal
- Try: `echo $PIXELLAB_API_KEY` and `echo $GEMINI_API_KEY`
- Or create a `.env` file with your keys

### Port already in use
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Kill process on port 5001
lsof -ti:5001 | xargs kill -9
```

## Architecture

```
┌─────────────────────┐
│  Browser (HTML/JS)  │
└──────────┬──────────┘
           │
           ├─────────────────────┐
           │                     │
           ▼                     ▼
┌──────────────────┐  ┌─────────────────────┐
│  PixelLab Bridge │  │   Nano Banana       │
│  (Port 5001)     │  │   (Port 5000)       │
└────────┬─────────┘  └──────────┬──────────┘
         │                       │
         ▼                       ▼
┌──────────────────┐  ┌─────────────────────┐
│  PixelLab API    │  │   Gemini API        │
│  (Pixel Art)     │  │   (Enhancement)     │
└──────────────────┘  └─────────────────────┘
```

## Cost Considerations

### PixelLab
- Charged per generation
- Check balance: `GET http://localhost:5001/get-balance`
- See pricing at https://www.pixellab.ai

### Gemini
- Free tier available
- Daily quotas apply
- See pricing at https://ai.google.dev/pricing

## Development

### Adding New Features
- Modify `sprite-enhancer.html` for UI changes
- Extend `pixellab_bridge_server.py` for PixelLab features
- Extend `nano_banana_server.py` for Gemini features

### Testing
```bash
# Test PixelLab server
curl http://localhost:5001/health

# Test Nano Banana server
curl http://localhost:5000/health
```

## Credits

- **PixelLab** - AI pixel art generation
- **Gemini** - Image enhancement
- Built for the AI-DnD project

## License

Part of the AI-DnD project. See main repository for license details.

---

**Enjoy creating and enhancing sprites!** 🎨✨

