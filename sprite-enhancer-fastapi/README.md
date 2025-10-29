# 🐍 Sprite Enhancer - FastAPI Full-Stack

**Modern Python full-stack application** for pixel art sprite generation and AI enhancement.

**Tech Stack:**
- **Backend:** FastAPI (Python 3.11+)
- **Database:** PostgreSQL
- **Frontend:** HTMX + Jinja2 Templates
- **Storage:** Local filesystem or AWS S3
- **APIs:** PixelLab + Google Gemini

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PixelLab API key
- Google Gemini API key

### 1. Clone and Setup

```bash
cd sprite-enhancer-fastapi

# Copy environment variables
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 2. Start with Docker Compose

```bash
# Start PostgreSQL + Backend
docker-compose up

# Visit http://localhost:8000
```

**That's it!** The app is running with PostgreSQL.

---

## 📦 Manual Setup (Without Docker)

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Mac/Linux
# or
venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

### 2. Setup PostgreSQL

```bash
# Install PostgreSQL (Mac)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb sprite_db
createuser sprite_user -P  # Enter password: sprite_pass
```

### 3. Run Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial tables"

# Run migrations
alembic upgrade head
```

### 4. Start Server

```bash
uvicorn app.main:app --reload

# Visit http://localhost:8000
```

---

## 🎯 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/token` - Login (get JWT token)
- `GET /api/auth/me` - Get current user

### Sprites
- `POST /api/sprites/generate` - Generate pixel art sprite
- `POST /api/sprites/{sprite_id}/enhance` - Enhance with AI
- `GET /api/sprites/{sprite_id}` - Get sprite by ID
- `DELETE /api/sprites/{sprite_id}` - Delete sprite

### History
- `GET /api/history` - Get user's sprite history
- `GET /api/history/count` - Get history count
- `DELETE /api/history/clear` - Clear all history

### System
- `GET /health` - Health check
- `GET /` - Web UI

---

## 📚 API Documentation

FastAPI automatically generates interactive API docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 🔧 Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql://sprite_user:sprite_pass@localhost:5432/sprite_db

# Security
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# API Keys
PIXELLAB_API_KEY=your_pixellab_key
GEMINI_API_KEY=your_gemini_key

# Storage (local or s3)
STORAGE_BACKEND=local
```

---

## 🗄️ Database Models

### User
- `id` - Primary key
- `email` - Unique email
- `username` - Unique username
- `hashed_password` - Bcrypt hash
- `is_active` - Account status
- `created_at` - Registration date

### Sprite
- `id` - Primary key
- `user_id` - Foreign key to User
- `prompt` - Generation prompt
- `image_url` - Image URL/path
- `size` - Image size (px)
- `style` - Style preset
- `created_at` - Creation date

### Enhanced
- `id` - Primary key
- `sprite_id` - Foreign key to Sprite (unique)
- `image_url` - Enhanced image URL
- `enhancement_prompt` - Enhancement description
- `style` - Enhancement style
- `generation_time` - Time taken (ms)
- `created_at` - Creation date

---

## 🎨 Usage Examples

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "pixelmaster",
    "password": "securepass123"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=securepass123"

# Response: {"access_token": "eyJ...", "token_type": "bearer"}
```

### 3. Generate Sprite

```bash
curl -X POST http://localhost:8000/api/sprites/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "fantasy knight with sword and shield",
    "size": 64
  }'
```

### 4. Enhance Sprite

```bash
curl -X POST http://localhost:8000/api/sprites/1/enhance \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "enhancement_prompt": "cinematic lighting, epic fantasy",
    "style": "photorealistic"
  }'
```

### 5. Get History

```bash
curl -X GET http://localhost:8000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/
```

---

## 🚢 Deployment

### Deploy to Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Deploy
railway up
```

### Deploy to Fly.io

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Launch app
fly launch

# Deploy
fly deploy
```

---

## 📊 Project Structure

```
sprite-enhancer-fastapi/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── database.py          # DB connection
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── sprites.py       # Sprite endpoints
│   │   │   └── history.py       # History endpoints
│   │   ├── services/
│   │   │   ├── pixellab.py      # PixelLab API
│   │   │   ├── gemini.py        # Gemini API
│   │   │   └── storage.py       # File storage
│   │   ├── templates/           # HTML templates
│   │   └── static/              # CSS/JS files
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── alembic/                     # Database migrations
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🎯 Features

### ✅ Implemented
- User authentication (JWT)
- Sprite generation (PixelLab)
- Image enhancement (Gemini)
- PostgreSQL storage
- Unlimited history
- RESTful API
- Auto-generated docs
- Docker support

### 🚧 Coming Soon
- HTMX frontend completion
- S3 storage integration
- Image galleries
- Sharing functionality
- API rate limiting
- WebSocket real-time updates

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file

---

## 🙏 Acknowledgments

- FastAPI for the amazing framework
- PixelLab for pixel art generation
- Google Gemini for AI enhancement
- HTMX for dynamic HTML

---

**Built with ❤️ using Python & FastAPI**

