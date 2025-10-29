# AI-DnD Image Generation API

[![PixelLab Integration](https://img.shields.io/badge/PixelLab-MCP%20Server-blue)](https://pixellab.ai)
[![Gemini Nano Banana](https://img.shields.io/badge/Gemini-Nano%20Banana-orange)](https://ai.google.dev/)

_Comprehensive image generation system for D&D scenes, characters, and items._

The AI-DnD Image Generation API provides two powerful image generation systems for creating artwork in your D&D adventures. Whether you need photorealistic scenes with Nano Banana or pixel art characters with PixelLab, we have you covered.

## 📚 Quick Links

- [Nano Banana API](#nano-banana-api) - Photorealistic D&D scenes and items
- [PixelLab API](#pixellab-api) - Pixel art generation via MCP
- [Code Examples](#code-examples) - Ready-to-use snippets
- [Troubleshooting](#troubleshooting) - Common issues and solutions

## Feature Comparison

| Feature | Nano Banana (FastAPI) | Nano Banana (Flask) | PixelLab |
|---------|----------------------|---------------------|----------|
| **Style** | Photorealistic | Photorealistic | Pixel Art |
| **Best For** | Scenes, Items, Production | Simple demos, testing | Characters, Sprites |
| **Model** | Gemini 2.5 Flash Image | Gemini 2.5 Flash Image | Pixflux/Bitforge |
| **Backend** | FastAPI + SQLite | Flask only | MCP Server |
| **Port** | 8000 | 5000 | N/A |
| **Database** | ✅ SQLite | ❌ None | ❌ N/A |
| **Scene Caching** | ✅ 7 days | ❌ Memory only | ❌ Not yet |
| **Image Storage** | ✅ WebP + Thumbnails | ❌ Base64 only | ✅ PNG |
| **Rate Limiting** | ✅ 10 req/min | ✅ 10 req/min | ✅ API-level |
| **Migrations** | ✅ Alembic | ❌ N/A | ❌ N/A |
| **Used By** | retro-adventure-game.html | Standalone demos | Cursor IDE |
| **Response Time** | ~3-5 seconds | ~3-5 seconds | ~5-10 seconds |

---

## Nano Banana API

Photorealistic image generation powered by Gemini's "Nano Banana" capabilities.

### Backend Options

**Two backends are available:**

1. **FastAPI Backend (Recommended - Production)** ⭐
   - Port: `8000`
   - Features: Database, caching, migrations, advanced features
   - Used by: `retro-adventure-game.html`
   - Setup: See [backend/README.md](../backend/README.md)

2. **Flask Backend (Simple - Standalone)**
   - Port: `5000`
   - Features: Basic image generation, rate limiting
   - Used by: Standalone demos
   - Setup: See [NANO_BANANA_QUICKSTART.md](../NANO_BANANA_QUICKSTART.md)

**This documentation covers the FastAPI backend (current production system).**

### Architecture

```
Frontend (JavaScript)          Backend (FastAPI)          Gemini API
─────────────────────          ─────────────────          ──────────
NanoBananaGenerator    ─────▶  FastAPI Server     ─────▶  Generate
   - generateSceneImage()      - /api/v1/images/*          Image
   - generateItemImage()       - /api/v1/scenes/*
   - Image caching             - SQLite database
   - Loading states            - WebP storage
                               - Scene caching (7 days)
```

### Backend Endpoints (FastAPI)

#### `GET /health`

Check server status and system health.

**Response:**
```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "disk_space": {
      "status": "ok",
      "free_gb": 123.45
    },
    "images": {
      "total": 42
    }
  }
}
```

#### `POST /api/v1/images/generate`

Generate an image and save to database.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `subject_type` | `string` | ✅ | `"scene"`, `"character"`, `"item"`, `"location"` |
| `subject_name` | `string` | ✅ | Name/title of the subject |
| `prompt` | `string` | ✅ | Detailed description of what to generate |
| `aspect_ratio` | `string` | ❌ | Image dimensions (default: `"1:1"`) |

**Valid Aspect Ratios:**
`"1:1"`, `"2:3"`, `"3:2"`, `"3:4"`, `"4:3"`, `"4:5"`, `"5:4"`, `"9:16"`, `"16:9"`, `"21:9"`

**Request Example:**
```json
{
  "subject_type": "location",
  "subject_name": "Dragon's Peak",
  "prompt": "Ancient dragon perched on mountain peak, misty valleys below, sunset lighting, fantasy art",
  "aspect_ratio": "16:9"
}
```

**Response:**
```json
{
  "id": 42,
  "subject_type": "location",
  "subject_name": "Dragon's Peak",
  "prompt": "Ancient dragon perched on mountain peak...",
  "image_url": "/images/42_dragons_peak.webp",
  "thumbnail_url": "/images/42_dragons_peak_thumb.webp",
  "aspect_ratio": "16:9",
  "created_at": "2025-10-29T12:34:56",
  "is_featured": false,
  "is_deleted": false
}
```

#### `POST /api/v1/scenes/generate`

Generate a scene with automatic caching (returns cached if exists).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | `string` | ✅ | Location name (e.g., "Emberpeak Village") |
| `time_of_day` | `string` | ❌ | `"dawn"`, `"day"`, `"dusk"`, `"night"` (default: `"day"`) |
| `weather` | `string` | ❌ | `"clear"`, `"rain"`, `"fog"`, `"storm"` (default: `"clear"`) |

**Caching:** Identical scenes are cached for 7 days. Returns cached version instantly if available.

**Request Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/scenes/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Emberpeak Village",
    "time_of_day": "dawn",
    "weather": "clear"
  }'
```

**Response:**
```json
{
  "scene_key": "emberpeak_village_dawn_clear",
  "image_data": "data:image/webp;base64,UklGR...",
  "cached": false,
  "cache_expires_at": "2025-11-05T12:34:56"
}
```

#### `GET /api/v1/images/search`

Search generated images with pagination.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | `number` | `1` | Page number |
| `page_size` | `number` | `12` | Items per page |
| `subject_type` | `string` | all | Filter by type |

**Request Example:**
```bash
curl "http://localhost:8000/api/v1/images/search?page=1&page_size=12&subject_type=item"
```

### Frontend API (NanoBananaGenerator)

JavaScript class for easy integration into web games.

#### Constructor

```javascript
const nanoBanana = new NanoBananaGenerator('http://localhost:8000/api/v1')
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `apiUrl` | `string` | `'http://localhost:8000/api/v1'` | Backend API base URL |

#### Methods

##### `generateSceneImage(prompt, options)`

Generate an image and return base64 data.

```javascript
const imageData = await nanoBanana.generateSceneImage(
  "Forest clearing with ancient stone circle",
  { aspectRatio: "16:9", cacheKey: "forest_clearing" }
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `prompt` | `string` | Image description |
| `options.aspectRatio` | `string` | Image dimensions (default: `"1:1"`) |
| `options.negativePrompt` | `string` | What to avoid |
| `options.cacheKey` | `string` | Enable caching with this key |

**Returns:** `Promise<string>` - Base64 image data or `null` on error

##### `generateItemImage(itemName)`

Generate artwork for an inventory item.

```javascript
const daggerArt = await nanoBanana.generateItemImage("Ancient Dagger")
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `itemName` | `string` | Item name |

**Returns:** `Promise<string>` - Base64 image data or `null`

##### `checkHealth()`

Check if backend server is available.

```javascript
const isHealthy = await nanoBanana.checkHealth()
```

**Returns:** `Promise<boolean>` - `true` if server is healthy

**Note:** Health endpoint is at `/health` (root level), not `/api/v1/health`

##### `displayImage(base64Data)`

Display generated image in the scene viewer.

```javascript
nanoBanana.displayImage(imageData)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `base64Data` | `string` | Complete data URI (e.g., `data:image/webp;base64,...`) |

**Returns:** `void`

**DOM Requirements:**
- Element with ID `scene-image` (image display)
- Element with ID `scene-fallback` (fallback display)
- Element with ID `scene-error` (error display)

#### Events

None. Uses async/await pattern for all operations.

### Code Examples

#### Basic Scene Generation

```javascript
// Initialize with FastAPI backend URL
const nanoBanana = new NanoBananaGenerator('http://localhost:8000/api/v1')

// Initialize and check server health
await nanoBanana.initialize()

// Generate scene
const imageData = await nanoBanana.generateSceneImage(
  "Torch-lit tavern interior, wooden tables, fantasy RPG setting",
  { aspectRatio: '16:9' }
)

// Display (displayImage is called automatically by generateSceneImage)
if (imageData) {
  console.log('Scene generated successfully!')
}
```

#### Item Image with Caching

```javascript
// Generate and cache
const swordImage = await nanoBanana.generateSceneImage(
  "Legendary greatsword with glowing runes",
  { cacheKey: "legendary_sword" }
)

// Subsequent calls return cached version instantly
const cachedImage = await nanoBanana.generateSceneImage(
  "Legendary greatsword with glowing runes",
  { cacheKey: "legendary_sword" }
)
```

#### Error Handling

```javascript
try {
  const image = await nanoBanana.generateSceneImage("...")
  if (!image) {
    console.log("Generation failed, showing fallback")
    showASCIIArt() // Fallback to ASCII art
  }
} catch (error) {
  console.error("Image generation error:", error)
}
```

---

## PixelLab API

Pixel art generation via Model Context Protocol (MCP) server.

### Setup

See [PIXELLAB_MCP_SETUP_COMPLETE.md](../PIXELLAB_MCP_SETUP_COMPLETE.md) for installation.

### MCP Tools

PixelLab provides several tools through the MCP server:

#### `generate_image_pixflux`

Generate pixel art from text description using Pixflux model.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | `string` | required | Text description of what to generate |
| `width` | `number` | `64` | Image width in pixels |
| `height` | `number` | `64` | Image height in pixels |
| `detail` | `string` | `"medium detail"` | `"low detail"` \| `"medium detail"` \| `"highly detailed"` |
| `shading` | `string` | `"basic shading"` | See shading options below |
| `outline` | `string` | `"single color black outline"` | See outline options below |
| `no_background` | `boolean` | `false` | Generate character without background |
| `text_guidance_scale` | `number` | `8` | How closely to follow prompt (1-20) |
| `save_to_file` | `string` | `undefined` | Optional file path to save |

**Shading Options:**
- `"flat shading"` - No shading
- `"basic shading"` - Simple light/dark
- `"medium shading"` - More detail
- `"detailed shading"` - Complex shadows
- `"highly detailed shading"` - Maximum detail

**Outline Options:**
- `"single color black outline"` - Classic pixel art
- `"single color outline"` - Colored outline
- `"selective outline"` - Only where needed
- `"lineless"` - No outlines

**Example:**
```json
{
  "description": "cute dragon with sword",
  "width": 64,
  "height": 64,
  "detail": "highly detailed",
  "shading": "detailed shading",
  "no_background": true
}
```

#### `generate_image_bitforge`

Generate pixel art using a reference style image.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | `string` | required | What to generate |
| `style_image_path` | `string` | required | Path to reference style image |
| `width` | `number` | `64` | Image width in pixels |
| `height` | `number` | `64` | Image height in pixels |
| `style_strength` | `number` | `50` | How strongly to match style (0-100) |
| `no_background` | `boolean` | `false` | Generate without background |
| `save_to_file` | `string` | `undefined` | Optional file path to save |

#### `rotate`

Rotate a character or object to face a different direction.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_path` | `string` | Path to character image |
| `to_direction` | `string` | Target direction |
| `from_direction` | `string` | Current direction (optional) |
| `width` | `number` | Output width (default: 64) |
| `height` | `number` | Output height (default: 64) |

**Directions:** `"south"`, `"south-east"`, `"east"`, `"north-east"`, `"north"`, `"north-west"`, `"west"`, `"south-west"`

#### `inpaint`

Edit specific regions using a mask.

| Parameter | Type | Description |
|-----------|------|-------------|
| `image_path` | `string` | Original pixel art image |
| `mask_path` | `string` | Mask (white = edit, black = keep) |
| `description` | `string` | What to paint in masked area |
| `width` | `number` | Output width (default: 64) |
| `height` | `number` | Output height (default: 64) |

#### `animate_with_text`

Create animated pixel art from text description.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | `string` | required | Character description |
| `action` | `string` | required | Action to animate (e.g., "walking") |
| `reference_image_path` | `string` | required | Reference character image |
| `n_frames` | `number` | `4` | Number of frames (1-20) |
| `direction` | `string` | `"east"` | Character facing direction |
| `view` | `string` | `"side"` | `"side"` \| `"low top-down"` \| `"high top-down"` |
| `width` | `number` | `64` | Frame width |
| `height` | `number` | `64` | Frame height |

### Code Examples

#### Generate Pixel Art Character

```python
# Via MCP tool (in Cursor or compatible IDE)
result = mcp_pixellab_generate_image_pixflux(
    description="brave knight with shield and sword",
    width=64,
    height=64,
    detail="highly detailed",
    shading="detailed shading",
    no_background=True,
    save_to_file="./knight.png"
)
```

#### Create Walking Animation

```python
# Generate reference character first
character = mcp_pixellab_generate_image_pixflux(
    description="pixel art wizard with staff",
    width=64,
    height=64,
    save_to_file="./wizard_base.png"
)

# Animate the character
animation = mcp_pixellab_animate_with_text(
    description="pixel art wizard with staff",
    action="walking",
    reference_image_path="./wizard_base.png",
    n_frames=4,
    direction="east",
    save_to_file="./wizard_walk.png"
)
```

---

## Troubleshooting

### Nano Banana Issues

**FastAPI Server won't start:**
- Check that `GEMINI_API_KEY` is set in `backend/.env`
- Verify port 8000 is not in use: `lsof -i :8000`
- Run database migrations: `cd backend && alembic upgrade head`
- Check Python dependencies: `pip install -r backend/requirements.txt`

**Images not generating:**
- Verify server health: `curl http://localhost:8000/health`
- Check database: Ensure `backend/dnd_game.db` exists
- Review server logs for API errors
- Check disk space: Images stored in `backend/images/`

**Frontend can't connect:**
- Ensure server is running on port 8000
- Check CORS configuration (allows localhost:8080, localhost:8000)
- Verify browser console for fetch errors
- Confirm API URL in `NanoBananaGenerator` constructor: `http://localhost:8000/api/v1`

**Flask Server Issues (if using standalone):**
- Port 5000 is used by Flask backend
- Check that `GEMINI_API_KEY` is in root `.env` file
- Run: `python nano_banana_server.py`
- Health check: `curl http://localhost:5000/health`

### PixelLab Issues

**MCP server not found:**
- Verify installation: Check `.cursor/mcp.json` configuration
- Restart Cursor/IDE to reload MCP servers
- Check API key is configured

**Generation fails:**
- Check account balance: Use `get_balance` tool
- Verify image dimensions (recommended: 32, 64, 128, 256)
- Try reducing `text_guidance_scale` if output is distorted

**Animation issues:**
- Ensure reference image exists and is readable
- Check that `n_frames` is between 1-20
- Verify `direction` is a valid compass direction

---

## Best Practices

### Performance

- **Cache aggressively:** Both systems support caching
- **Batch requests:** Generate multiple images during loading screens
- **Fallback content:** Always have ASCII art or placeholder ready
- **Rate limiting:** Respect API limits (10/min for Nano Banana)

### Prompts

**Nano Banana (Photorealistic):**
```
Good: "Medieval tavern interior, stone walls, roaring fireplace, wooden tables,
       warm lighting, fantasy RPG setting, cinematic composition"

Bad:  "tavern"
```

**PixelLab (Pixel Art):**
```
Good: "brave knight character, blue armor, holding sword and shield,
       single color black outline, medium shading"

Bad:  "make it look cool"
```

### Integration

- Generate images asynchronously during loading
- Show loading states with themed animations
- Provide fallback content for offline/error states
- Log generation metrics for monitoring

---

## Additional Resources

- [Nano Banana Usage Guide](../NANO_BANANA_USAGE.md)
- [Nano Banana Quick Start](../NANO_BANANA_QUICKSTART.md)
- [PixelLab MCP Setup](../PIXELLAB_MCP_SETUP_COMPLETE.md)
- [Item Image Generation Feature](../ITEM_IMAGE_GENERATION_FEATURE.md)

---

**Last Updated:** October 29, 2025
**API Version:** Nano Banana 1.0, PixelLab MCP 1.0

