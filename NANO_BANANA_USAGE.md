# Nano Banana Image Generation - Usage Guide

## Overview
The retro adventure game now includes AI-powered image generation using Gemini's "Nano Banana" capabilities. This feature generates photorealistic D&D scenes, character portraits, and item artwork to enhance the gaming experience.

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `google-genai` - Gemini API SDK
- `flask` - Web server
- `flask-cors` - CORS support
- `python-dotenv` - Environment variable management
- `pillow` - Image processing

### 2. Configure API Key
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_api_key_here
```

Get your API key from: https://ai.google.dev/

### 3. Start the Backend Server
```bash
python nano_banana_server.py
```

You should see:
```
🍌 Nano Banana Image Generation Server
✓ API Key configured
✓ Running on http://localhost:5000
✓ Rate limit: 10 requests/minute
```

### 4. Open the Game
Open `retro-adventure-game.html` in your browser. The game will automatically:
- Check if the backend server is available
- Generate the Emberpeak entrance scene
- Display it in the Scene Viewer panel

## Architecture

### Backend Server (`nano_banana_server.py`)
Flask microservice that handles all Gemini API interactions:
- Securely stores API key
- Processes image generation requests
- Returns base64-encoded images
- Implements rate limiting
- Provides detailed error messages

### Frontend Module (`NanoBananaGenerator`)
JavaScript class integrated into the game:
- Communicates with backend via fetch API
- Manages image caching
- Handles loading/error states
- Provides ASCII art fallbacks
- Exposes clean, reusable API

## API Reference

### Backend Endpoints

#### `GET /health`
Check server status and API key configuration.

**Response:**
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "client_initialized": true
}
```

#### `POST /generate-image`
Generate an image from a detailed prompt.

**Request:**
```json
{
  "prompt": "A photorealistic scene description...",
  "aspect_ratio": "16:9",
  "response_modalities": ["Image"]
}
```

**Response:**
```json
{
  "success": true,
  "image": "base64_encoded_image_data",
  "generation_time": 2.5
}
```

#### `POST /generate-scene`
Generate a D&D scene with sensible defaults.

**Request:**
```json
{
  "description": "The entrance to Emberpeak village at dawn",
  "style": "photorealistic",
  "aspect_ratio": "16:9"
}
```

**Styles:**
- `photorealistic` - Realistic photography style
- `fantasy_art` - Detailed fantasy artwork
- `comic` - Comic book illustration
- `pixel_art` - Pixel art style

### Frontend API

#### `generateSceneImage(prompt, options)`
Generate a scene image.

```javascript
await nanoBanana.generateSceneImage(
    'a mystical forest clearing with ancient ruins',
    {
        style: 'fantasy_art',
        aspectRatio: '16:9'
    }
);
```

#### `generateCharacterPortrait(characterData)`
Generate a character portrait.

```javascript
await nanoBanana.generateCharacterPortrait({
    name: 'Thorin Ironforge',
    class: 'Dwarf Fighter',
    description: 'Grizzled warrior with a long beard and battle scars'
});
```

#### `generateItemImage(itemName)`
Generate item artwork.

```javascript
await nanoBanana.generateItemImage('Ancient Sword of Fire');
```

## Usage Examples

### Example 1: Generate Location Image
```javascript
// Generate an image for the current location
const location = gameState.locations[gameState.currentLocation];
const prompt = `${location.description}, fantasy RPG setting, atmospheric lighting`;

await nanoBanana.generateSceneImage(prompt, {
    style: 'photorealistic',
    aspectRatio: '16:9'
});
```

### Example 2: Generate Combat Scene
```javascript
// Generate a dramatic combat scene
const combatPrompt = `A fierce battle between a rogue and goblins in a dark mine tunnel, torchlight, action scene`;

await nanoBanana.generateSceneImage(combatPrompt, {
    style: 'fantasy_art',
    aspectRatio: '16:9'
});
```

### Example 3: Generate NPC Portrait
```javascript
// Create a portrait of an NPC
await nanoBanana.generateCharacterPortrait({
    name: 'Foreman Garrett',
    class: 'Human Commoner',
    description: 'Middle-aged miner, weathered face, hard hat, worried expression'
});
```

### Example 4: Item Inspection
```javascript
// Show detailed artwork when examining an item
const item = itemDatabase['Sealing Stone'];
await nanoBanana.generateItemImage(
    `${item.description}, glowing blue runes, mystical artifact`
);
```

## Features

### Image Caching
Images are cached client-side to avoid redundant API calls:
```javascript
// First call generates image
await nanoBanana.generateSceneImage('emberpeak entrance');

// Second call uses cached version (instant)
await nanoBanana.generateSceneImage('emberpeak entrance');

// Clear cache if needed
nanoBanana.clearCache();
```

### Error Handling
Graceful fallback to ASCII art when generation fails:
```
🏔️  EMBERPEAK VILLAGE  🏔️
═══════════════════════════
     /\        /\
    /  \      /  \
   /    \    /    \
  /      \  /      \
 /________\/________\
 |  🚪  ||  🏠  |
 |      ||      |
═════════════════════
     WELCOME
```

### Loading States
Visual feedback during generation:
- Animated loading message: "Generating scene with Nano Banana..."
- Loading spinner in Scene Viewer panel
- Success message in Adventure Log
- Error messages if generation fails

### Rate Limiting
Backend enforces 10 requests per minute to prevent API abuse. Exceeding the limit returns:
```json
{
  "error": "Rate limit exceeded. Maximum 10 requests per minute."
}
```

## Supported Aspect Ratios

| Ratio | Resolution | Use Case |
|-------|------------|----------|
| 1:1 | 1024x1024 | Portraits, items, icons |
| 16:9 | 1344x768 | Scenes, landscapes (default) |
| 9:16 | 768x1344 | Vertical scenes, portraits |
| 4:3 | 1184x864 | Classic screen ratio |
| 21:9 | 1536x672 | Ultra-wide cinematic |

## Troubleshooting

### Server Not Starting
```bash
# Check if API key is configured
cat .env

# Should contain:
GEMINI_API_KEY=your_key_here
```

### Images Not Generating
1. Verify server is running: `curl http://localhost:5000/health`
2. Check browser console for errors (F12)
3. Verify API key has proper permissions
4. Check rate limiting hasn't been exceeded

### Port Already in Use
```bash
# Kill existing process
lsof -ti:5000 | xargs kill -9

# Or change port in nano_banana_server.py:
app.run(debug=True, host='0.0.0.0', port=5001)

# Update frontend in retro-adventure-game.html:
const nanoBanana = new NanoBananaGenerator('http://localhost:5001');
```

### CORS Errors
The server includes CORS headers. If issues persist:
```python
# In nano_banana_server.py, modify CORS config:
CORS(app, resources={r"/*": {"origins": "*"}})
```

## Performance Tips

1. **Cache Aggressively**: Images are cached automatically, but you can preload common scenes:
   ```javascript
   // Preload common locations
   await nanoBanana.generateSceneImage('tavern interior');
   await nanoBanana.generateSceneImage('forest path');
   await nanoBanana.generateSceneImage('mine entrance');
   ```

2. **Use Appropriate Aspect Ratios**: Square (1:1) for portraits/items, wide (16:9) for scenes

3. **Optimize Prompts**: More detailed prompts produce better results:
   - ❌ Bad: "tavern"
   - ✅ Good: "dimly lit medieval tavern, wooden tables, fireplace, warm atmosphere"

4. **Monitor Rate Limits**: The 10 requests/minute limit prevents API abuse

## Future Enhancements

Planned features:
- [ ] Real-time scene generation as player moves
- [ ] NPC portrait generation from dialogue
- [ ] Combat scene visualization
- [ ] Item inspection with generated artwork
- [ ] Multi-turn image editing
- [ ] Image style selection UI
- [ ] Batch generation for multiple scenes
- [ ] Progressive image loading
- [ ] Image gallery/history viewer
- [ ] Save/export generated images

## Security Notes

- ✅ API key stored in .env (gitignored)
- ✅ Rate limiting prevents abuse
- ✅ CORS configured for security
- ✅ No API key exposed to frontend
- ✅ SynthID watermark included in all images

## Credits

- **Gemini API**: Google's generative AI platform
- **Nano Banana**: Gemini's image generation feature
- **Flask**: Python web framework
- **Integration**: Built for AI D&D Adventure Game

## Support

For issues or questions:
1. Check the [Gemini API Documentation](https://ai.google.dev/gemini-api/docs/image-generation)
2. Review browser console logs (F12)
3. Check server logs in terminal
4. Verify API key and permissions

## License

This integration follows the same license as the main project.

