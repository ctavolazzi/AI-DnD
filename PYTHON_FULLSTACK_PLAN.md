# 🐍 Python Full-Stack Architecture Plan

**Date:** October 28, 2025
**Stack:** Python everywhere (Backend + Frontend framework)

---

## 🎯 Python Full-Stack Options

Since you're already in Python, here are the BEST Python-based stacks:

### **Option 1: FastAPI + React/HTMX (Recommended)**
```
Backend: FastAPI (Modern Python)
├── Async/await support
├── Auto-generated docs (Swagger)
├── Type hints with Pydantic
└── WebSocket support

Frontend: HTMX (or React if you prefer)
├── HTMX = HTML over the wire (very Python-friendly)
├── Or React for richer UI
└── Tailwind CSS for styling

Database: PostgreSQL
├── SQLAlchemy ORM
├── Alembic migrations
└── Unlimited storage

Deployment: Fly.io or Railway
├── Free tier available
├── Easy Docker deployment
└── PostgreSQL included
```

### **Option 2: Django + Django REST + React**
```
Backend: Django (Batteries included)
├── Built-in admin panel
├── Django ORM
├── User authentication
└── Django REST Framework for APIs

Frontend: React + Tailwind
├── Component-based UI
├── Modern tooling
└── Better UX than vanilla JS

Benefits:
✅ All-in-one framework
✅ Admin panel out of the box
✅ Mature ecosystem
⚠️ Heavier than FastAPI
```

### **Option 3: FastAPI + HTMX (Simplest)**
```
Backend: FastAPI
Frontend: HTMX (HTML templates)
├── Jinja2 templates
├── HTMX for dynamic updates
└── No React/Node.js needed!

Benefits:
✅ All Python, no JavaScript build step
✅ Server-rendered HTML
✅ Fast development
✅ Easy to understand
```

---

## 🚀 Recommended: FastAPI + HTMX

**Why this is perfect for your use case:**

1. ✅ **All Python** - No Node.js needed
2. ✅ **Fast development** - Write less code
3. ✅ **Modern** - Async, type hints, auto-docs
4. ✅ **Simple deployment** - Single Docker container
5. ✅ **Perfect for AI apps** - Easy to integrate with APIs

---

## 📁 Project Structure

```
sprite-enhancer/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # DB connection
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── sprites.py       # Sprite generation endpoints
│   │   │   ├── auth.py          # User authentication
│   │   │   └── history.py       # History endpoints
│   │   ├── services/
│   │   │   ├── pixellab.py      # PixelLab integration
│   │   │   ├── gemini.py        # Gemini integration
│   │   │   └── storage.py       # S3/Cloudinary storage
│   │   └── templates/           # Jinja2 HTML templates
│   │       ├── base.html
│   │       ├── index.html
│   │       └── components/
│   ├── alembic/                 # Database migrations
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── htmx.min.js
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 💻 Code Examples

### **1. FastAPI Main App** (`app/main.py`)

```python
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db, engine
from app.routers import sprites, auth, history
from app import models

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sprite Enhancer API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sprites.router, prefix="/api/sprites", tags=["sprites"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

@app.get("/")
async def root(request: Request, db: Session = Depends(get_db)):
    """Main page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
```

### **2. Database Models** (`app/models.py`)

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sprites = relationship("Sprite", back_populates="user")

class Sprite(Base):
    __tablename__ = "sprites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    prompt = Column(Text)
    image_url = Column(String)  # S3 URL
    size = Column(Integer, default=64)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="sprites")
    enhanced = relationship("Enhanced", back_populates="sprite", uselist=False)

class Enhanced(Base):
    __tablename__ = "enhanced"

    id = Column(Integer, primary_key=True, index=True)
    sprite_id = Column(Integer, ForeignKey("sprites.id"), unique=True)
    image_url = Column(String)  # S3 URL
    style = Column(String)
    prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sprite = relationship("Sprite", back_populates="enhanced")
```

### **3. Sprite Router** (`app/routers/sprites.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.services import pixellab, gemini, storage
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/generate", response_model=schemas.SpriteResponse)
async def generate_sprite(
    request: schemas.SpriteRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Generate a pixel art sprite"""

    # Call PixelLab API
    sprite_data = await pixellab.generate(
        prompt=request.prompt,
        size=request.size
    )

    # Upload to S3 in background
    image_url = await storage.upload_image(
        sprite_data,
        f"sprites/{current_user.id}/{request.prompt[:30]}.png"
    )

    # Save to database
    db_sprite = models.Sprite(
        user_id=current_user.id,
        prompt=request.prompt,
        image_url=image_url,
        size=request.size
    )
    db.add(db_sprite)
    db.commit()
    db.refresh(db_sprite)

    return db_sprite

@router.post("/{sprite_id}/enhance", response_model=schemas.EnhancedResponse)
async def enhance_sprite(
    sprite_id: int,
    request: schemas.EnhanceRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Enhance a sprite with Gemini"""

    # Get sprite
    sprite = db.query(models.Sprite).filter(
        models.Sprite.id == sprite_id,
        models.Sprite.user_id == current_user.id
    ).first()

    if not sprite:
        raise HTTPException(status_code=404, detail="Sprite not found")

    # Download original sprite
    sprite_image = await storage.download_image(sprite.image_url)

    # Call Gemini API
    enhanced_data = await gemini.enhance(
        sprite_image,
        prompt=request.prompt,
        style=request.style
    )

    # Upload to S3
    image_url = await storage.upload_image(
        enhanced_data,
        f"enhanced/{current_user.id}/{sprite_id}.png"
    )

    # Save to database
    db_enhanced = models.Enhanced(
        sprite_id=sprite_id,
        image_url=image_url,
        style=request.style,
        prompt=request.prompt
    )
    db.add(db_enhanced)
    db.commit()
    db.refresh(db_enhanced)

    return db_enhanced
```

### **4. HTMX Frontend** (`app/templates/index.html`)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Sprite Enhancer</title>
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    <link href="/static/css/styles.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <h1>The Sprite Tavern</h1>

        <!-- Generate Form -->
        <form hx-post="/api/sprites/generate"
              hx-target="#sprite-result"
              hx-indicator="#loading">
            <textarea name="prompt" placeholder="Describe your sprite..."></textarea>
            <select name="size">
                <option value="64">64x64</option>
                <option value="128">128x128</option>
            </select>
            <button type="submit">Generate</button>
        </form>

        <div id="loading" class="htmx-indicator">Generating...</div>

        <!-- Result -->
        <div id="sprite-result"></div>

        <!-- History -->
        <div hx-get="/api/history"
             hx-trigger="load"
             hx-target="#history-list">
            <h2>History</h2>
            <div id="history-list"></div>
        </div>
    </div>
</body>
</html>
```

---

## 🗄️ Database Setup

### **PostgreSQL with Docker Compose**

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: sprite_user
      POSTGRES_PASSWORD: sprite_pass
      POSTGRES_DB: sprite_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: .
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://sprite_user:sprite_pass@db:5432/sprite_db
      PIXELLAB_API_KEY: ${PIXELLAB_API_KEY}
      GEMINI_API_KEY: ${GEMINI_API_KEY}

volumes:
  postgres_data:
```

---

## 📦 Requirements

```txt
# requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic==2.5.3
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.26.0
pillow==10.2.0
boto3==1.34.34  # For S3
jinja2==3.1.3
```

---

## 🚀 Quick Start Commands

```bash
# Create project
mkdir sprite-enhancer && cd sprite-enhancer
python -m venv venv
source venv/bin/activate  # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Setup database
docker-compose up -d db

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Visit
open http://localhost:8000
```

---

## 🎯 Benefits Over Current Setup

| Feature | Current | FastAPI + PostgreSQL |
|---------|---------|---------------------|
| **Storage** | localStorage (10MB) | PostgreSQL (unlimited) |
| **History** | 10 sprites | Thousands |
| **Users** | None | Full auth system |
| **Sync** | Local only | Cross-device |
| **Speed** | Fast | Faster (async) |
| **Deployment** | Manual | Docker one-command |
| **Cost** | Free | Free tier (Railway/Fly.io) |
| **Maintenance** | 2 servers | 1 unified API |

---

## 🔄 Migration Path

### **Phase 1: Setup Backend** (2-3 hours)
1. Create FastAPI project structure
2. Setup PostgreSQL with Docker
3. Create database models
4. Port PixelLab/Gemini logic

### **Phase 2: Build API** (3-4 hours)
1. Sprite generation endpoint
2. Enhancement endpoint
3. History endpoints
4. User authentication

### **Phase 3: Frontend** (2-3 hours)
1. Port current HTML to Jinja2 templates
2. Add HTMX for dynamic updates
3. Connect to new API

### **Phase 4: Storage** (1-2 hours)
1. Setup S3 or Cloudinary
2. Upload images instead of base64
3. Serve via CDN

### **Total:** ~10-12 hours for complete migration

---

## 🎨 Want Me To Build It?

I can scaffold the entire FastAPI project right now:
- ✅ Project structure
- ✅ Database models
- ✅ API routes
- ✅ HTMX templates
- ✅ Docker setup
- ✅ Migration from current code

**Should I start?** 🚀

