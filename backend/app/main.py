"""FastAPI main application"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from datetime import datetime
import shutil
from pathlib import Path

from .config import settings
from .database import engine, Base, get_db
from .api import images_router, scenes_router, maintenance_router, migrate_router, game_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="D&D Image Generation API",
    description="AI-powered image generation for D&D adventures with caching and persistence",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "null"  # Allow file:// origins for local development
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    allow_credentials=False  # Must be False when allowing "null" origin
)

# Include API routers
app.include_router(images_router)
app.include_router(scenes_router)
app.include_router(maintenance_router)
app.include_router(migrate_router)
app.include_router(game_router)

# Serve static images
images_path = Path(settings.IMAGE_STORAGE_DIR)
if images_path.exists():
    app.mount("/images", StaticFiles(directory=str(images_path)), name="images")

# Serve frontend (if exists)
frontend_path = Path("../retro-adventure-game.html")
if frontend_path.parent.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path.parent)), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "D&D Image Generation API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health():
    """
    Health check endpoint with system details

    Checks:
    - Database connectivity
    - Disk space
    - Image count
    """
    from sqlalchemy.orm import Session
    from sqlalchemy import text
    from .models.image_asset import ImageAsset

    # Check database
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        db_status = "ok"

        # Check image count
        image_count = db.query(ImageAsset).filter(ImageAsset.deleted_at == None).count()
        db.close()
    except Exception as e:
        db_status = "error"
        image_count = -1

    # Check disk space
    try:
        disk = shutil.disk_usage(".")
        disk_free_gb = round(disk.free / (1024**3), 2)
        disk_status = "ok" if disk_free_gb > 1 else "warning"
    except:
        disk_free_gb = -1
        disk_status = "error"

    overall_status = "ok"
    if db_status == "error" or disk_status == "error":
        overall_status = "error"
    elif disk_status == "warning":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": db_status,
            "disk_space": {
                "status": disk_status,
                "free_gb": disk_free_gb
            },
            "images": {
                "total": image_count
            }
        }
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "code": 404,
            "message": "Endpoint not found",
            "path": str(request.url.path)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "code": 500,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

