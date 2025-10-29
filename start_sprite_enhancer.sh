#!/bin/bash
# Start Sprite Enhancer - Launches both servers and opens the web app

echo "🎨 Starting Sprite Enhancer..."
echo ""

# Check for API keys
if [ -z "$PIXELLAB_API_KEY" ]; then
    echo "⚠️  WARNING: PIXELLAB_API_KEY not set"
    echo "   Set it with: export PIXELLAB_API_KEY='your-key'"
    echo ""
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  WARNING: GEMINI_API_KEY not set"
    echo "   Set it with: export GEMINI_API_KEY='your-key'"
    echo ""
fi

# Check if ports are available
if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5001 is already in use. Kill the process? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        lsof -ti:5001 | xargs kill -9
        echo "✓ Port 5001 cleared"
    else
        echo "❌ Cannot start PixelLab server"
        exit 1
    fi
fi

if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 5000 is already in use. Kill the process? (y/n)"
    read -r response
    if [ "$response" = "y" ]; then
        lsof -ti:5000 | xargs kill -9
        echo "✓ Port 5000 cleared"
    else
        echo "❌ Cannot start Nano Banana server"
        exit 1
    fi
fi

echo ""
echo "Starting servers..."
echo ""

# Start PixelLab Bridge Server (port 5001)
echo "📡 Starting PixelLab Bridge Server (port 5001)..."
python3 pixellab_bridge_server.py > logs/pixellab_bridge.log 2>&1 &
PIXELLAB_PID=$!
sleep 2

# Start Nano Banana Server (port 5000)
echo "🍌 Starting Nano Banana Server (port 5000)..."
python3 nano_banana_server.py > logs/nano_banana.log 2>&1 &
BANANA_PID=$!
sleep 2

# Check if servers started successfully
if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ PixelLab Bridge Server failed to start"
    echo "   Check logs/pixellab_bridge.log for details"
    exit 1
fi

if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "❌ Nano Banana Server failed to start"
    echo "   Check logs/nano_banana.log for details"
    kill $PIXELLAB_PID
    exit 1
fi

echo ""
echo "✅ All servers running!"
echo ""
echo "┌────────────────────────────────────────┐"
echo "│  PixelLab Bridge:  http://localhost:5001"
echo "│  Nano Banana:      http://localhost:5000"
echo "└────────────────────────────────────────┘"
echo ""
echo "Opening Sprite Enhancer in browser..."
open sprite-enhancer.html

echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Trap Ctrl+C to clean up
trap "echo ''; echo 'Stopping servers...'; kill $PIXELLAB_PID $BANANA_PID; echo '✓ Servers stopped'; exit 0" INT

# Keep script running
wait

