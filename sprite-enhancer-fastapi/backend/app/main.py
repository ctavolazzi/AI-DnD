"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.database import engine
from app import models
from app.routers import sprites, auth, history

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Mount uploads directory (if using local storage)
if settings.storage_backend == "local":
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sprites.router, prefix="/api/sprites", tags=["Sprites"])
app.include_router(history.router, prefix="/api/history", tags=["History"])


@app.get("/")
async def root(request: Request):
    """Main page - Sprite Enhancer UI."""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "title": settings.app_name}
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "pixellab_configured": settings.pixellab_api_key is not None,
        "gemini_configured": settings.gemini_api_key is not None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )

