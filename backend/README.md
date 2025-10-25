# D&D Image Generation Backend

FastAPI backend with SQLite database for AI-powered D&D adventure image generation, caching, and persistence.

## Features

- **Image Generation**: AI-powered image generation via Gemini 2.5 Flash Image
- **Scene Caching**: Automatic caching of generated scenes (7-day expiry)
- **Filesystem Storage**: WebP compression with thumbnail generation
- **Rate Limiting**: Built-in rate limiting (10 req/min for images, 5 req/min for scenes)
- **Migration Support**: One-click migration from LocalStorage
- **Maintenance Tools**: Automated cleanup and backup scripts

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access Application

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Images

- `POST /api/v1/images/generate` - Generate new image
- `GET /api/v1/images/search` - Search images (paginated)
- `GET /api/v1/images/{id}` - Get specific image
- `PUT /api/v1/images/{id}/feature` - Toggle featured status
- `DELETE /api/v1/images/{id}` - Soft delete image

### Scenes

- `POST /api/v1/scenes/generate` - Generate/retrieve cached scene
- `GET /api/v1/scenes/cache/stats` - Cache statistics
- `DELETE /api/v1/scenes/cache/clear` - Clear cache

### Maintenance

- `POST /api/v1/maintenance/cleanup/expired-cache` - Delete expired cache
- `POST /api/v1/maintenance/cleanup/orphaned-images` - Delete old images
- `GET /api/v1/maintenance/stats` - System statistics

### Migration

- `POST /api/v1/migrate/from-localstorage` - Migrate LocalStorage data

## Database Management

### Create Migration

```bash
alembic revision --autogenerate -m "Description of changes"
# IMPORTANT: Review generated migration file before applying!
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback Migration

```bash
alembic downgrade -1
```

## Backup & Restore

### Create Backup

```bash
./scripts/backup.sh
```

### Automated Backups (Cron)

Add to crontab:

```bash
# Daily backup at 2 AM
0 2 * * * cd /path/to/backend && ./scripts/backup.sh
```

### Restore from Backup

```bash
# Decompress backup
gunzip backups/dnd_game_20241025_140000.db.gz

# Restore database
cp backups/dnd_game_20241025_140000.db dnd_game.db

# Restart server
```

## Maintenance Tasks

### Cleanup Expired Cache

```bash
curl -X POST http://localhost:8000/api/v1/maintenance/cleanup/expired-cache
```

### Cleanup Orphaned Images

```bash
curl -X POST http://localhost:8000/api/v1/maintenance/cleanup/orphaned-images
```

### View Statistics

```bash
curl http://localhost:8000/api/v1/maintenance/stats
```

## Configuration

Environment variables (`.env`):

```bash
# Required
GEMINI_API_KEY=your_api_key_here

# Database
DATABASE_URL=sqlite:///./dnd_game.db

# Storage
IMAGE_STORAGE_DIR=images
MAX_IMAGE_SIZE_MB=5
MAX_IMAGES_PER_ITEM=20

# Caching
CACHE_EXPIRY_DAYS=7

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=10

# Image Processing
THUMBNAIL_SIZE=(200, 200)
WEBP_QUALITY=85

# Backup
BACKUP_RETENTION_DAYS=30
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Returns:
- Database status
- Disk space
- Image count

### Metrics

Prometheus metrics available at:

```
http://localhost:8000/metrics
```

## Development

### Run Tests

```bash
pytest
```

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload
```

### Enable SQL Logging

Edit `app/database.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    echo=True  # Set to True for SQL logging
)
```

## Architecture

```
backend/
├── app/
│   ├── api/            # API endpoints
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── services/       # Business logic
│   ├── config.py       # Configuration
│   ├── database.py     # Database setup
│   └── main.py         # FastAPI app
├── alembic/            # Database migrations
├── images/             # Image storage
│   ├── full/           # Full size images
│   └── thumbnails/     # Thumbnail images
├── backups/            # Database backups
└── tests/              # Test suite
```

## Performance

Expected performance metrics:

- **Image Retrieval**: < 50ms (filesystem + database lookup)
- **Scene Cache Lookup**: < 20ms (indexed database query)
- **Image Generation**: 3-8s (Gemini API dependent)
- **Database Queries**: < 20ms average

## Troubleshooting

### Database Locked Error

SQLite uses StaticPool to serialize writes. If you see "database is locked" errors:

1. Check for long-running transactions
2. Reduce concurrent write operations
3. Consider upgrading to PostgreSQL for production

### Out of Disk Space

Check disk usage:

```bash
du -sh images/
```

Run cleanup:

```bash
curl -X POST http://localhost:8000/api/v1/maintenance/cleanup/orphaned-images
```

### Rate Limit Errors

Adjust rate limits in `.env`:

```bash
MAX_REQUESTS_PER_MINUTE=20  # Increase from default 10
```

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub.

