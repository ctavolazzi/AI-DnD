# Migration Guide: localStorage → FastAPI Backend

## Overview

**Current State:**
- Game uses Nano Banana server (port 5000)
- Images cached in `new Map()` (in-memory only)
- Lost on page refresh ❌

**Target State:**
- Game uses FastAPI backend (port 8000)
- Images stored in SQLite database + filesystem
- Persist forever ✅

---

## Phase 1: Backend Setup (30 minutes)

### 1.1 Configure Backend

```bash
cd backend

# Create .env file
cat > .env << 'EOF'
GEMINI_API_KEY=your_actual_api_key_here
EOF

# Install dependencies
pip install -r requirements.txt

# Run migrations
python -m alembic upgrade head
```

### 1.2 Start Backend

```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend runs at: **http://localhost:8000**

### 1.3 Verify Backend

```bash
# Test health
curl http://localhost:8000/health

# Run test suite
python test_backend.py
```

Expected: All tests pass ✅

---

## Phase 2: Seed Database (20 minutes)

### 2.1 Generate All Game Images

```bash
# Backend must be running first
cd backend
python seed_game_assets.py
```

This generates and stores 18 scene images (~2-3 minutes).

**What happens:**
- Checks database for existing images
- Generates only missing ones
- Stores in `backend/dnd_game.db` + `backend/images/`
- Images persist forever

### 2.2 Verify Seeding

```bash
# Check database
curl http://localhost:8000/api/v1/images/search?subject_type=scene

# View in browser
open http://localhost:8000/docs
```

---

## Phase 3: Update Frontend (1-2 hours)

### 3.1 Change API URL

**File:** `retro-adventure-game.html`

```javascript
// Line ~2263
class NanoBananaGenerator {
    constructor(apiUrl = 'http://localhost:5000') {  // OLD
    constructor(apiUrl = 'http://localhost:8000/api/v1') {  // NEW
```

### 3.2 Update Cache to Use Database

**Current (in-memory):**
```javascript
// Line ~2265
this.imageCache = new Map();  // Lost on refresh
```

**Option A: Remove cache entirely (backend handles it)**
```javascript
// Delete this.imageCache completely
// Backend caches in database automatically
```

**Option B: Keep Map for session cache**
```javascript
this.imageCache = new Map();  // Session-only cache
// Backend DB is source of truth
```

### 3.3 Update Image Generation Logic

**File:** `retro-adventure-game.html` (~line 2307)

**Before:**
```javascript
async generateSceneImage(prompt, options = {}) {
    const cacheKey = `scene_${prompt}_${aspectRatio}`;

    // Check in-memory cache
    if (this.imageCache.has(cacheKey)) {
        return this.imageCache.get(cacheKey);
    }

    // Generate via Nano Banana
    const response = await fetch(`${this.apiUrl}/generate-scene`, {
        method: 'POST',
        body: JSON.stringify({
            description: prompt,
            style: options.style || 'photorealistic',
            aspect_ratio: aspectRatio
        })
    });
}
```

**After:**
```javascript
async generateSceneImage(prompt, options = {}) {
    const subjectName = options.subjectName || prompt;

    // 1. Search database first
    const searchUrl = `${this.apiUrl}/images/search?subject_name=${encodeURIComponent(subjectName)}&subject_type=scene`;
    const searchResp = await fetch(searchUrl);
    const searchData = await searchResp.json();

    if (searchData.total > 0) {
        // Found in database!
        console.log('📦 Using cached image from database');
        const image = searchData.items[0];
        return {
            imageUrl: `data:image/webp;base64,${image.base64_data}`,
            cached: true,
            metadata: image
        };
    }

    // 2. Generate if doesn't exist
    console.log('🎨 Generating new image...');
    const response = await fetch(`${this.apiUrl}/images/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            subject_type: 'scene',
            subject_name: subjectName,
            prompt: prompt,
            aspect_ratio: options.aspectRatio || '16:9',
            component: 'scene-viewer',
            custom_prompt: options.customPrompt
        })
    });

    if (!response.ok) {
        throw new Error(`Generation failed: ${response.status}`);
    }

    const data = await response.json();
    return {
        imageUrl: `data:image/webp;base64,${data.base64_data}`,
        cached: false,
        metadata: data
    };
}
```

### 3.4 Update Scene Initialization

**File:** `retro-adventure-game.html` (~line 3574)

**Before:**
```javascript
const scenePrompt = 'the entrance to Emberpeak...';
const result = await nanoBanana.generateSceneImage(scenePrompt, {...});
```

**After:**
```javascript
const result = await nanoBanana.generateSceneImage(
    'the entrance to Emberpeak...',
    {
        subjectName: 'Emberpeak Entrance',  // Must match seeded name
        style: 'photorealistic',
        aspectRatio: '16:9'
    }
);
```

### 3.5 Update Item Image Generation

**File:** `retro-adventure-game.html` (~line 3666)

Similar changes for item images - use `subject_type: 'item'` instead of `'scene'`.

---

## Phase 4: Testing (30 minutes)

### 4.1 Test Scene Loading

1. Open game: `open retro-adventure-game.html`
2. Check console - should see: `📦 Using cached image from database`
3. No "Generating..." messages (unless database was empty)

### 4.2 Test Image Persistence

1. Refresh page
2. Images load instantly from database
3. No API calls made (check Network tab)

### 4.3 Test Server Restart

1. Stop backend (Ctrl+C)
2. Start backend again
3. Refresh game page
4. Images still load instantly ✅

---

## Phase 5: Cleanup (15 minutes)

### 5.1 Deprecate Nano Banana

Once frontend uses FastAPI backend:

```bash
# Optional: Archive old server
mv nano_banana_server.py legacy/
```

### 5.2 Update Documentation

```bash
# Update README.md
# Remove references to port 5000
# Update quickstart to use backend only
```

### 5.3 Single Command Startup

Create `start.sh`:
```bash
#!/bin/bash
cd backend
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Backend running at http://localhost:8000"
echo "Opening game..."
sleep 2
open http://localhost:8000/static/retro-adventure-game.html

# Wait for Ctrl+C
trap "kill $BACKEND_PID" EXIT
wait
```

---

## Architecture Comparison

### Before (Current)

```
┌─────────────────────┐
│ retro-adventure-    │
│ game.html           │ (port 8080)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Nano Banana Server  │ (port 5000)
│ Flask + Map cache   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Gemini API          │
└─────────────────────┘

Cache: Map (in-memory) ❌
Persistence: None ❌
```

### After (Target)

```
┌─────────────────────┐
│ retro-adventure-    │
│ game.html           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ FastAPI Backend     │ (port 8000)
│ + SQLite DB         │
│ + File Storage      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Gemini API          │
└─────────────────────┘

Cache: Database ✅
Persistence: Forever ✅
```

---

## Benefits After Migration

| Feature | Before | After |
|---------|--------|-------|
| Persistence | Lost on refresh | Forever |
| Multi-browser | No | Yes |
| Storage | Browser RAM | Database + Files |
| Analytics | None | Full tracking |
| Thumbnails | No | Auto-generated |
| Compression | No | WebP (85% quality) |
| Rate limiting | Basic | Sophisticated |
| Search | No | Full queries |
| Backups | No | Database backups |
| API docs | No | Swagger UI |

---

## Rollback Plan

If something goes wrong:

1. **Keep both servers running temporarily**
   ```bash
   # Terminal 1: Old (Nano Banana)
   python nano_banana_server.py

   # Terminal 2: New (FastAPI)
   cd backend && uvicorn app.main:app --reload
   ```

2. **Frontend can switch API URL easily**
   ```javascript
   // Use environment variable or config
   const API_URL = process.env.USE_NEW_BACKEND
       ? 'http://localhost:8000/api/v1'
       : 'http://localhost:5000';
   ```

3. **Test both in parallel**
   - Open game with old API
   - Open game with new API
   - Compare behavior

---

## Estimated Timeline

- ✅ Phase 1 (Backend setup): 30 minutes
- ✅ Phase 2 (Seed database): 20 minutes
- ⏳ Phase 3 (Update frontend): 1-2 hours ← **YOU ARE HERE**
- ⏳ Phase 4 (Testing): 30 minutes
- ⏳ Phase 5 (Cleanup): 15 minutes

**Total:** 2.5-3.5 hours for complete migration

---

## Next Steps

**Option A: Automated Migration Script**
- Create script to auto-update frontend API calls
- One-click migration
- **Time:** 2-3 hours to build script

**Option B: Manual Migration**
- Follow Phase 3 steps above
- Update `retro-adventure-game.html` manually
- **Time:** 1-2 hours

**Option C: Gradual Migration**
- Keep both servers running
- Migrate one component at a time
- Test each change
- **Time:** 3-4 hours (safer)

---

**Your call! Which approach do you prefer?**

