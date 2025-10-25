# FastAPI Backend Migration Plan

## Executive Summary

**Goal:** Migrate from in-memory image caching to persistent database storage

**Current Problem:** Images regenerate every page refresh, wasting API quota
**Solution:** Use FastAPI backend with SQLite database for permanent storage
**Timeline:** 2-3 hours active work
**Risk Level:** Low (can run both systems in parallel)

---

## Phase 0: Current State Assessment

### What We Have

#### Frontend (Working)
- `retro-adventure-game.html` - Main game
- Uses `NanoBananaGenerator` class
- Points to `http://localhost:5000` (Nano Banana server)
- Caches in `new Map()` (in-memory only)
- **Problem:** Cache lost on page refresh

#### Nano Banana Server (Working)
- `nano_banana_server.py` - Flask server (port 5000)
- Uses `gemini-2.5-flash-image` model ✅
- No persistence layer
- **Problem:** Every session regenerates same images

#### FastAPI Backend (Prepared, Not Running)
- `backend/` directory with complete implementation
- SQLite database with `image_assets` and `scene_cache` tables
- WebP compression + thumbnail generation
- Rate limiting and analytics
- **Status:** ✅ Fixed Gemini model, ready to test

### What's Missing

1. ❌ Backend `.env` file (needs GEMINI_API_KEY)
2. ❌ Database not initialized
3. ❌ No images in database yet
4. ❌ Frontend still points to old server
5. ❌ No testing of backend functionality

---

## Phase 1: Backend Validation (30 minutes)

**Goal:** Verify FastAPI backend works before touching game

### 1.1 Environment Setup (5 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Create .env file
cat > .env << 'EOF'
# Gemini API Configuration
GEMINI_API_KEY=<COPY_FROM_NANO_BANANA_ENV>

# Database (default is fine)
DATABASE_URL=sqlite:///./dnd_game.db

# Storage (defaults are fine)
IMAGE_STORAGE_DIR=images
CACHE_EXPIRY_DAYS=7
MAX_REQUESTS_PER_MINUTE=10
EOF
```

**How to get API key:**
```bash
# Check if nano banana has it
grep GEMINI_API_KEY ../.env 2>/dev/null
# Or check environment
echo $GEMINI_API_KEY
```

**Success Criteria:**
- ✅ `.env` file exists with valid API key

---

### 1.2 Install Dependencies (5 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Install Python packages
pip install -r requirements.txt
```

**Expected packages:**
- fastapi
- uvicorn
- sqlalchemy
- alembic
- pillow (image processing)
- slowapi (rate limiting)
- google-genai (Gemini)
- pydantic-settings

**Success Criteria:**
- ✅ All packages install without errors
- ✅ No conflicts

---

### 1.3 Database Initialization (5 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Run migrations
python -m alembic upgrade head
```

**What this creates:**
- `dnd_game.db` - SQLite database file
- `images/` - Storage directory
- Database tables:
  - `image_assets` - Generated images
  - `scene_cache` - Scene cache with expiry

**Success Criteria:**
- ✅ `dnd_game.db` file exists
- ✅ `images/` directory exists
- ✅ No migration errors

---

### 1.4 Start Backend (2 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Start server
uvicorn app.main:app --reload --port 8000
```

**Leave this terminal running**

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Success Criteria:**
- ✅ Server starts without errors
- ✅ Accessible at http://localhost:8000

---

### 1.5 Health Check (2 min)

**New terminal:**
```bash
# Test health endpoint
curl http://localhost:8000/health

# Should return:
# {
#   "status": "ok",
#   "checks": {
#     "database": "ok",
#     "disk_space": {"status": "ok", "free_gb": ...},
#     "images": {"total": 0}
#   }
# }
```

**Or open in browser:**
```bash
open http://localhost:8000/docs
```

**Success Criteria:**
- ✅ Health check returns `"status": "ok"`
- ✅ Database status is `"ok"`
- ✅ Interactive docs load

---

### 1.6 Run Test Suite (10 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Run automated tests
python test_backend.py
```

**What this tests:**
1. Backend connectivity
2. Image search (should find 0 images)
3. Image generation (generates 1 test image)
4. Image retrieval
5. Database persistence

**Expected output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Health Check
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Backend is healthy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  3. Generate New Image
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⏳ Generating test image...
✅ Image generated successfully!
   ID: 1
   Time: 8.23s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ All tests passed!
```

**Success Criteria:**
- ✅ All 5 tests pass
- ✅ One test image generated and stored
- ✅ Image persists in database

---

### Phase 1 Checkpoint

**Before proceeding to Phase 2:**
- [ ] Backend running at http://localhost:8000
- [ ] Health check returns "ok"
- [ ] Test suite passes
- [ ] Database has 1 test image

**If any test fails:** STOP and debug before continuing

---

## Phase 2: Database Seeding (20 minutes)

**Goal:** Pre-generate all 18 game scene images

### 2.1 Run Seeding Script (15-20 min)

```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend

# Backend must be running in another terminal
python seed_game_assets.py
```

**What this does:**
- Checks database for each of 18 scenes
- Generates only missing scenes
- Stores in database + `images/` directory
- 2-second delay between generations (avoid rate limits)

**Expected output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GAME ASSETS SEEDER (FastAPI Backend)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Backend is running

📋 Seeding 18 game scenes...

[1/18] Emberpeak Entrance...
   ✅ Generated (1234 KB, 8234ms)
[2/18] Starting Tavern...
   ✅ Generated (1156 KB, 7891ms)
[3/18] Town Square...
   ✅ Generated (1289 KB, 8456ms)
...
[18/18] Deep Chamber...
   ✅ Generated (1445 KB, 9123ms)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SEEDING COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Generated:      18
⚡ Already cached: 0
❌ Failed:         0
📊 Total:          18
⏱️  Time:           156.2s
```

**Timeline:**
- ~8-10 seconds per image
- 18 images total
- ~2-3 minutes total time

---

### 2.2 Verify Seeding (2 min)

```bash
# Check database
curl "http://localhost:8000/api/v1/images/search?subject_type=scene" | jq

# Should show 18 images
# {
#   "items": [...],
#   "total": 18,
#   "page": 1,
#   "page_size": 12
# }
```

**Or via API docs:**
```bash
open http://localhost:8000/docs
# Try: GET /api/v1/images/search
# Set subject_type = scene
# Should return 18 items
```

**Check filesystem:**
```bash
ls -lh backend/images/
# Should show 18 .webp files + 18 thumbnails
```

**Success Criteria:**
- ✅ 18 images in database
- ✅ 36 files in `images/` directory (18 full + 18 thumbnails)
- ✅ Total size ~15-25 MB

---

### Phase 2 Checkpoint

**Before proceeding to Phase 3:**
- [ ] 18 scenes generated successfully
- [ ] Database query returns all 18
- [ ] Files exist in `backend/images/`
- [ ] No generation failures

**If seeding failed:** Run script again (it will skip cached images)

---

## Phase 3: Parallel Testing (30 minutes)

**Goal:** Test backend API with game WITHOUT modifying game yet

### 3.1 Keep Both Servers Running

**Terminal 1: Nano Banana (old)**
```bash
cd /Users/ctavolazzi/Code/AI-DnD
python nano_banana_server.py
# Port 5000
```

**Terminal 2: FastAPI (new)**
```bash
cd /Users/ctavolazzi/Code/AI-DnD/backend
uvicorn app.main:app --reload --port 8000
# Port 8000
```

**Both should be running simultaneously**

---

### 3.2 Manual API Testing (10 min)

**Test retrieving a scene:**
```bash
# Get "Emberpeak Entrance" (this is the game's starting scene)
curl "http://localhost:8000/api/v1/images/search?subject_name=Emberpeak%20Entrance" | jq

# Expected: Returns 1 image with base64 data
```

**Test scene cache:**
```bash
# Check cache stats
curl "http://localhost:8000/api/v1/scenes/cache/stats" | jq

# Expected:
# {
#   "total_scenes": 18,
#   "active_cache_entries": 18,
#   "expired": 0,
#   "cache_hit_rate": 0.00
# }
```

**Test maintenance endpoints:**
```bash
# Get system stats
curl "http://localhost:8000/api/v1/maintenance/stats" | jq
```

---

### 3.3 Compare Response Formats (10 min)

**Nano Banana response:**
```bash
curl -X POST http://localhost:5000/generate-scene \
  -H "Content-Type: application/json" \
  -d '{"description": "test", "aspect_ratio": "16:9"}'
```

**FastAPI response:**
```bash
curl -X POST http://localhost:8000/api/v1/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "subject_type": "scene",
    "subject_name": "Test Scene",
    "prompt": "test",
    "aspect_ratio": "16:9",
    "component": "test"
  }'
```

**Document differences:**
- Field names
- Response structure
- Base64 data location
- Metadata format

**This informs frontend changes needed**

---

### Phase 3 Checkpoint

**Before proceeding to Phase 4:**
- [ ] Both servers running simultaneously
- [ ] Can retrieve images via API
- [ ] Response format documented
- [ ] No errors in logs

---

## Phase 4: Frontend Migration (1-2 hours)

**Goal:** Update game to use FastAPI backend

### 4.1 Create Backup (2 min)

```bash
cp retro-adventure-game.html retro-adventure-game.html.backup-$(date +%Y%m%d)
```

**Success Criteria:**
- ✅ Backup file created
- ✅ Original can be restored if needed

---

### 4.2 Update API URL (5 min)

**File:** `retro-adventure-game.html`
**Line:** ~2263

**Change:**
```javascript
// OLD:
constructor(apiUrl = 'http://localhost:5000') {

// NEW:
constructor(apiUrl = 'http://localhost:8000/api/v1') {
```

**Save but don't test yet**

---

### 4.3 Update generateSceneImage Method (30 min)

**File:** `retro-adventure-game.html`
**Line:** ~2307

**Current implementation:**
- Checks in-memory Map
- Calls `/generate-scene`
- Stores in Map

**New implementation:**
1. Search database first (`GET /images/search`)
2. If found, return cached
3. If not found, generate (`POST /images/generate`)
4. Store in database automatically

**Detailed code changes in MIGRATION_GUIDE.md Section 3.3**

---

### 4.4 Update Scene Initialization (15 min)

**File:** `retro-adventure-game.html`
**Line:** ~3574

**Add `subjectName` to options:**
```javascript
const result = await nanoBanana.generateSceneImage(
    'the entrance to Emberpeak...',
    {
        subjectName: 'Emberpeak Entrance',  // NEW: Must match seeded name
        style: 'photorealistic',
        aspectRatio: '16:9'
    }
);
```

**This ensures cache lookup works**

---

### 4.5 Update Item Image Generation (15 min)

**File:** `retro-adventure-game.html`
**Line:** ~3666

**Similar changes for items:**
- Add `subjectName`
- Use `subject_type: 'item'`
- Search before generating

---

### 4.6 Update CORS if Needed (5 min)

**File:** `backend/app/main.py`
**Lines:** 34-46

**May need to add:**
```python
allow_origins=[
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "file://*",  # NEW: For local HTML files
],
```

---

### Phase 4 Checkpoint

**Before proceeding to Phase 5:**
- [ ] Backup created
- [ ] API URL updated
- [ ] generateSceneImage updated
- [ ] Scene initialization updated
- [ ] No syntax errors (check browser console)

---

## Phase 5: Testing & Validation (30 minutes)

**Goal:** Verify everything works with new backend

### 5.1 First Load Test (10 min)

```bash
# Ensure FastAPI backend is running
# Terminal 1:
cd backend
uvicorn app.main:app --reload

# Open game
open retro-adventure-game.html
```

**Check browser console:**
```
Expected messages:
✅ "📦 Using cached image from database"
✅ NO "🎨 Generating new image"
✅ Scene loads instantly
❌ NO errors
```

**If you see errors:**
- Check Network tab for failed requests
- Check backend logs for errors
- Verify CORS settings
- Check API URL is correct

---

### 5.2 Cache Hit Test (5 min)

**Refresh page multiple times:**
- Images should load instantly every time
- Console shows "Using cached image from database"
- No API generation calls
- Network tab shows only search queries (very fast)

**Success Criteria:**
- ✅ Images load <100ms
- ✅ No generation API calls
- ✅ No errors

---

### 5.3 Server Restart Test (5 min)

1. **Stop backend** (Ctrl+C in backend terminal)
2. **Refresh game page** (should fail gracefully)
3. **Restart backend**
4. **Refresh game page** (should work immediately)

**Success Criteria:**
- ✅ Images still in database after restart
- ✅ No regeneration needed
- ✅ Instant load on restart

---

### 5.4 Browser Cache Test (5 min)

1. **Clear browser cache** (Cmd+Shift+Delete)
2. **Refresh page**

**Success Criteria:**
- ✅ Images still load (from backend, not browser cache)
- ✅ No regeneration

---

### 5.5 New Image Generation Test (5 min)

**Try generating a NEW scene (not in database):**

```javascript
// In browser console:
await nanoBanana.generateSceneImage(
    'A mysterious castle on a cliff',
    {
        subjectName: 'Mystery Castle',
        aspectRatio: '16:9'
    }
);
```

**Expected:**
1. Searches database (not found)
2. Generates new image (~8-10 seconds)
3. Stores in database
4. Next request is instant (cached)

**Success Criteria:**
- ✅ Generation works
- ✅ Image stored in database
- ✅ Second request is instant

---

### Phase 5 Checkpoint

**Before proceeding to Phase 6:**
- [ ] First load works
- [ ] Cache hits work
- [ ] Server restart works
- [ ] Browser cache clear works
- [ ] New generation works

**If any test fails:** Revert to backup and debug

---

## Phase 6: Cleanup & Documentation (15 minutes)

**Goal:** Finalize migration and clean up

### 6.1 Deprecate Nano Banana (5 min)

**Once everything works with FastAPI:**

```bash
# Stop Nano Banana server
# (Ctrl+C in terminal)

# Optional: Archive it
mkdir -p legacy
mv nano_banana_server.py legacy/
```

**Update README.md:**
- Remove references to port 5000
- Update quickstart to use backend only
- Document new architecture

---

### 6.2 Create Startup Script (5 min)

**File:** `start.sh`
```bash
#!/bin/bash
cd backend
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Backend running at http://localhost:8000"
echo "Opening game..."
sleep 2
open ../retro-adventure-game.html

trap "kill $BACKEND_PID" EXIT
wait
```

```bash
chmod +x start.sh
```

**Usage:**
```bash
./start.sh  # One command to start everything
```

---

### 6.3 Update Documentation (5 min)

**Files to update:**
- `README.md` - New quickstart
- `QUICKSTART.md` - Backend instructions
- `AGENTS.md` - Architecture notes

**Remove:**
- References to Nano Banana
- Port 5000 instructions
- In-memory cache limitations

**Add:**
- Backend setup steps
- Database seeding instructions
- Persistence benefits

---

### Phase 6 Checkpoint

**Migration complete when:**
- [ ] Nano Banana deprecated
- [ ] Startup script works
- [ ] Documentation updated
- [ ] Team aware of changes

---

## Rollback Plan

**If something goes wrong at any phase:**

### Quick Rollback
```bash
# 1. Restore backup
cp retro-adventure-game.html.backup-YYYYMMDD retro-adventure-game.html

# 2. Start Nano Banana
python nano_banana_server.py

# 3. Open game
open retro-adventure-game.html
```

**Everything works as before** ✅

---

### Gradual Rollback

**Keep both systems running:**
```bash
# Terminal 1: Nano Banana (backup)
python nano_banana_server.py

# Terminal 2: FastAPI (new)
cd backend && uvicorn app.main:app --reload
```

**Toggle between them:**
```javascript
// In game HTML, add config:
const USE_NEW_BACKEND = false;  // Toggle this
const API_URL = USE_NEW_BACKEND
    ? 'http://localhost:8000/api/v1'
    : 'http://localhost:5000';
```

---

## Timeline Summary

| Phase | Description | Time | Risk |
|-------|-------------|------|------|
| 0 | Current state assessment | 10 min | None |
| 1 | Backend validation | 30 min | Low |
| 2 | Database seeding | 20 min | Low |
| 3 | Parallel testing | 30 min | None |
| 4 | Frontend migration | 1-2 hours | Medium |
| 5 | Testing & validation | 30 min | Low |
| 6 | Cleanup & docs | 15 min | None |

**Total Active Work:** 2.5-3.5 hours
**Waiting Time:** ~3 minutes (image generation)
**Total Elapsed:** 3-4 hours

---

## Success Criteria

### Must Have ✅
- [ ] Backend runs without errors
- [ ] All 18 scenes in database
- [ ] Game loads scenes from database
- [ ] Images persist across restarts
- [ ] No regeneration on refresh

### Should Have ✅
- [ ] Cache hit rate >90%
- [ ] Load time <100ms per image
- [ ] Error handling works
- [ ] API docs accessible
- [ ] Test script passes

### Nice to Have ✨
- [ ] Startup script works
- [ ] Documentation updated
- [ ] Nano Banana deprecated
- [ ] Team trained on new system

---

## Risk Assessment

### Low Risk ✅
- Backend is separate (doesn't affect current game)
- Can run both servers in parallel
- Easy rollback (restore backup)
- Changes are isolated

### Medium Risk ⚠️
- Frontend API changes could break game
- CORS issues might arise
- API response format differences

### Mitigation ✅
- Keep backup of original file
- Test thoroughly before deprecating old system
- Keep both servers running during migration
- Document all changes

---

## Post-Migration Benefits

### Immediate
- ✅ Images persist forever
- ✅ No regeneration on refresh
- ✅ Saves API quota
- ✅ Faster load times

### Long-term
- ✅ Analytics on image usage
- ✅ Multi-browser support
- ✅ Database backups
- ✅ Better error handling
- ✅ Rate limiting protection
- ✅ Thumbnail generation
- ✅ WebP compression
- ✅ Scalable architecture

---

## Decision Points

### After Phase 1: Backend Validation
**If backend doesn't work:**
- Stop and fix issues
- Don't proceed to seeding
- No impact on current game

### After Phase 2: Database Seeding
**If seeding fails:**
- Fix API issues
- Adjust rate limits
- Re-run seeding script
- No impact on current game

### After Phase 4: Frontend Migration
**If game breaks:**
- Restore backup immediately
- Revert to Nano Banana
- Debug issues
- Try again when ready

### After Phase 5: Testing
**If tests fail:**
- Don't deprecate Nano Banana yet
- Keep both systems running
- Fix issues gradually
- Full rollback available

---

## Communication Plan

### Before Migration
- ✅ Review plan with team
- ✅ Schedule migration time
- ✅ Prepare rollback steps
- ✅ Backup everything

### During Migration
- ✅ Document issues encountered
- ✅ Keep logs of all changes
- ✅ Test after each phase
- ✅ Stop if major issues arise

### After Migration
- ✅ Document what was learned
- ✅ Update team on new system
- ✅ Archive old system
- ✅ Monitor for issues

---

## Next Steps

### Immediate (Today)
1. Read this plan completely
2. Decide on migration timing
3. Verify prerequisites (API key, Python, etc.)

### Short-term (This Week)
1. Execute Phase 1 (backend validation)
2. Execute Phase 2 (database seeding)
3. Plan frontend migration timing

### Long-term (This Month)
1. Complete frontend migration
2. Deprecate old system
3. Document lessons learned
4. Plan future enhancements

---

## Questions to Answer Before Starting

1. **Do we have the GEMINI_API_KEY?**
   - Check: `echo $GEMINI_API_KEY`
   - Or: `grep GEMINI_API_KEY .env`

2. **Is Python 3.9+ installed?**
   - Check: `python --version`

3. **Do we have ~50MB disk space?**
   - Check: `df -h .`

4. **Can we afford 2-3 hours of focused work?**
   - Best done in one sitting
   - Avoid context switching

5. **Is there a backup plan if things go wrong?**
   - Yes: Keep Nano Banana running
   - Yes: Restore backup file
   - Yes: Rollback is easy

---

## Final Checklist

**Before starting Phase 1:**
- [ ] Read entire plan
- [ ] Understand each phase
- [ ] Have API key ready
- [ ] Have 2-3 hours available
- [ ] Know how to rollback
- [ ] Comfortable with risk level

**After completing all phases:**
- [ ] Game works with new backend
- [ ] Images persist across restarts
- [ ] Old system deprecated
- [ ] Documentation updated
- [ ] Team trained
- [ ] Monitoring in place

---

**Status:** PLAN COMPLETE - READY TO EXECUTE ✅

**Next Action:** Review plan, then execute Phase 1 when ready.


