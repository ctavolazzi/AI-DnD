#!/bin/bash
# Start FastAPI development server

echo "🚀 Starting D&D Image Generation Backend..."
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found"
    echo "Please create .env file with your GEMINI_API_KEY"
    echo "Example: cp .env.template .env"
    exit 1
fi

# Check if database exists
if [ ! -f "dnd_game.db" ]; then
    echo "⚠️  Database not found, running migrations..."
    alembic upgrade head
    echo ""
fi

# Start server
echo "✓ Configuration loaded"
echo "✓ Starting server on http://localhost:8000"
echo ""
echo "Available endpoints:"
echo "  - http://localhost:8000       (API info)"
echo "  - http://localhost:8000/docs  (Interactive API docs)"
echo "  - http://localhost:8000/health (Health check)"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

