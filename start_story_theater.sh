#!/bin/bash

# Interactive Story Theater - Quick Start Script
# Starts all required servers and opens the browser

echo "📖 Starting Interactive Story Theater..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if required files exist
if [ ! -f "dnd_narrative_server.py" ]; then
    echo -e "${RED}❌ Error: dnd_narrative_server.py not found${NC}"
    exit 1
fi

if [ ! -f "nano_banana_server.py" ]; then
    echo -e "${RED}❌ Error: nano_banana_server.py not found${NC}"
    exit 1
fi

if [ ! -f "interactive-story-theater.html" ]; then
    echo -e "${RED}❌ Error: interactive-story-theater.html not found${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "   Create .env with: GEMINI_API_KEY=your_key_here"
    echo ""
fi

# Create Obsidian vault directory if it doesn't exist
if [ ! -d "ai-dnd-test-vault" ]; then
    echo -e "${YELLOW}📁 Creating Obsidian vault directory...${NC}"
    mkdir -p ai-dnd-test-vault/Stories
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Shutting down servers...${NC}"
    kill $NARRATIVE_PID 2>/dev/null
    kill $IMAGE_PID 2>/dev/null
    echo -e "${GREEN}✅ All servers stopped${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Narrative Server (port 5002)
echo -e "${GREEN}🎭 Starting Narrative Server (port 5002)...${NC}"
python3 dnd_narrative_server.py > logs/narrative_server.log 2>&1 &
NARRATIVE_PID=$!
echo "   PID: $NARRATIVE_PID"

# Wait a moment for server to start
sleep 2

# Start Nano Banana Image Server (port 5000)
echo -e "${GREEN}🎨 Starting Image Generation Server (port 5000)...${NC}"
python3 nano_banana_server.py > logs/image_server.log 2>&1 &
IMAGE_PID=$!
echo "   PID: $IMAGE_PID"

# Wait for servers to initialize
echo ""
echo -e "${YELLOW}⏳ Waiting for servers to initialize...${NC}"
sleep 3

# Check if servers are running
if ! ps -p $NARRATIVE_PID > /dev/null; then
    echo -e "${RED}❌ Narrative server failed to start${NC}"
    echo "   Check logs/narrative_server.log for details"
    exit 1
fi

if ! ps -p $IMAGE_PID > /dev/null; then
    echo -e "${RED}❌ Image server failed to start${NC}"
    echo "   Check logs/image_server.log for details"
    kill $NARRATIVE_PID 2>/dev/null
    exit 1
fi

echo ""
echo -e "${GREEN}✅ All servers running!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📖 Interactive Story Theater"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Servers:"
echo "   Narrative:  http://localhost:5002"
echo "   Images:     http://localhost:5000"
echo ""
echo "📁 Story saves to: ai-dnd-test-vault/Stories/"
echo ""
echo "🎮 Opening browser..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Open the browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "interactive-story-theater.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "interactive-story-theater.html"
else
    echo "Please open interactive-story-theater.html manually"
fi

# Keep script running
echo "📊 Server logs:"
echo "   Narrative: tail -f logs/narrative_server.log"
echo "   Images:    tail -f logs/image_server.log"
echo ""

# Wait for user to press Ctrl+C
wait

