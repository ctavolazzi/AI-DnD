# FastAPI Backend Setup

## Prerequisites

- Python 3.9+
- Gemini API key from https://ai.google.dev/

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend/` directory:

```bash
# backend/.env
GEMINI_API_KEY=your_actual_api_key_here
```

**Required:**
- `GEMINI_API_KEY`: Your Gemini API key

**Optional (with defaults):**
- `DATABASE_URL=sqlite:///./dnd_game.db`
- `IMAGE_STORAGE_DIR=images`
- `MAX_REQUESTS_PER_MINUTE=10`
- `CACHE_EXPIRY_DAYS=7`

### 3. Initialize Database

```bash
# Run migrations
cd backend
python -m alembic upgrade head
```

This creates:
- `dnd_game.db` (SQLite database)
- `images/` directory for storage

### 4. Start Server

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

Server runs at: **http://localhost:8000**

### 5. Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs
```

Expected response:
```json
{
  "status": "ok",
  "checks": {
    "database": "ok",
    "disk_space": {"status": "ok", "free_gb": 123.45},
    "images": {"total": 0}
  }
}
```

## API Endpoints

### Core Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation

### Image Management

- `POST /api/v1/images/generate` - Generate new image
- `GET /api/v1/images/search` - Search existing images
- `GET /api/v1/images/{id}` - Get specific image
- `PUT /api/v1/images/{id}/feature` - Toggle featured status
- `DELETE /api/v1/images/{id}` - Soft delete image

### Scene Caching

- `POST /api/v1/scenes/generate` - Generate/retrieve cached scene
- `GET /api/v1/scenes/cache/stats` - Cache statistics
- `DELETE /api/v1/scenes/cache/clear` - Clear cache

### Maintenance

- `GET /api/v1/maintenance/stats` - System statistics
- `POST /api/v1/maintenance/cleanup` - Clean up old files
- `POST /api/v1/maintenance/backup` - Create backup

### Migration

- `POST /api/v1/migrate/from-localstorage` - Migrate from localStorage

## Testing

```bash
cd backend
pytest tests/ -v
```

Expected: 4 tests passing

## Troubleshooting

### "GEMINI_API_KEY not set"

Create `.env` file in `backend/` directory with your API key.

### "Database not found"

Run migrations: `python -m alembic upgrade head`

### "Permission denied" on images/

```bash
mkdir -p backend/images
chmod 755 backend/images
```

### "Port 8000 already in use"

```bash
# Find process
lsof -i :8000

# Kill it or use different port
uvicorn app.main:app --port 8001
```

## Next Steps

Once backend is running:

1. Test image generation via API docs (http://localhost:8000/docs)
2. Run seeding script (see `MIGRATION_GUIDE.md`)
3. Update frontend to use backend API
4. Deprecate Nano Banana server

