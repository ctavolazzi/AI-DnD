#!/bin/bash

# Narrative Theater Startup Script
# Starts all required servers for the DnD Narrative Theater experience

echo "🎭 Starting DnD Narrative Theater Servers..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  No virtual environment found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo -e "${BLUE}📦 Installing narrative theater requirements...${NC}"
pip install -q -r narrative_theater_requirements.txt
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}✅ Requirements installed${NC}"
echo ""

# Check if Ollama is running
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found. Please install Ollama from https://ollama.ai${NC}"
    echo ""
fi

# Function to check if port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Kill any existing servers on our ports
echo -e "${BLUE}🧹 Cleaning up old processes...${NC}"
for port in 5000 5001 5002; do
    if check_port $port; then
        echo "  Stopping process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

echo ""

# Start servers in background
echo -e "${GREEN}🚀 Starting servers...${NC}"
echo ""

# 1. Nano Banana Server (port 5000)
echo -e "${BLUE}[1/3]${NC} Starting Nano Banana Server (port 5000)..."
python3 nano_banana_server.py > logs/nano_banana.log 2>&1 &
NANO_PID=$!
echo "  PID: $NANO_PID"
sleep 2

# 2. PixelLab Bridge Server (port 5001)
echo -e "${BLUE}[2/3]${NC} Starting PixelLab Bridge Server (port 5001)..."
python3 pixellab_bridge_server.py > logs/pixellab_bridge.log 2>&1 &
PIXELLAB_PID=$!
echo "  PID: $PIXELLAB_PID"
sleep 2

# 3. DnD Narrative Server (port 5002)
echo -e "${BLUE}[3/3]${NC} Starting DnD Narrative Server (port 5002)..."
python3 dnd_narrative_server.py > logs/narrative_server.log 2>&1 &
NARRATIVE_PID=$!
echo "  PID: $NARRATIVE_PID"
sleep 3

echo ""
echo -e "${GREEN}✅ All servers started!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎭 NARRATIVE THEATER IS READY! 🎲${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Server Status:"
echo "  🎨 Nano Banana:       http://localhost:5000  (PID: $NANO_PID)"
echo "  🎮 PixelLab Bridge:   http://localhost:5001  (PID: $PIXELLAB_PID)"
echo "  📖 Narrative Server:  http://localhost:5002  (PID: $NARRATIVE_PID)"
echo ""
echo "Open in your browser:"
echo -e "  ${BLUE}file://$(pwd)/dnd-narrative-theater.html${NC}"
echo ""
echo "Logs:"
echo "  logs/nano_banana.log"
echo "  logs/pixellab_bridge.log"
echo "  logs/narrative_server.log"
echo ""
echo "To stop all servers, press Ctrl+C or run:"
echo "  ./stop_narrative_theater.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save PIDs for cleanup script
echo "$NANO_PID" > .narrative_theater_pids
echo "$PIXELLAB_PID" >> .narrative_theater_pids
echo "$NARRATIVE_PID" >> .narrative_theater_pids

# Wait for user to stop (Ctrl+C)
trap cleanup INT TERM

cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Stopping servers...${NC}"
    kill $NANO_PID $PIXELLAB_PID $NARRATIVE_PID 2>/dev/null
    rm -f .narrative_theater_pids
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

# Keep script running
wait

