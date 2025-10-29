#!/bin/bash

echo "🚀 Starting Gemini Chat Interface..."
echo ""
echo "📖 Quick Setup:"
echo "   1. Get your API key: https://aistudio.google.com/app/apikey"
echo "   2. Paste it in the input field"
echo "   3. Click 'Connect'"
echo "   4. Start chatting!"
echo ""
echo "🎨 Pro Tip: Try the different themes!"
echo "💡 Pro Tip: Open the console (F12) for advanced features!"
echo ""

# Start a simple HTTP server
PORT=8000

echo "🌐 Starting local server on http://localhost:${PORT}"
echo ""
echo "✨ Opening browser..."
echo "   If it doesn't open automatically, visit: http://localhost:${PORT}"
echo ""
echo "⚠️  Press Ctrl+C to stop the server"
echo ""

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sleep 1 && open "http://localhost:${PORT}" &
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sleep 1 && xdg-open "http://localhost:${PORT}" &
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash, Cygwin, MSYS)
    sleep 1 && start "http://localhost:${PORT}" &
fi

# Start Python HTTP server (works on most systems)
if command -v python3 &> /dev/null; then
    python3 -m http.server ${PORT}
elif command -v python &> /dev/null; then
    python -m http.server ${PORT}
else
    echo "❌ Error: Python is not installed."
    echo "   Please install Python or open index.html with a local server."
    exit 1
fi
