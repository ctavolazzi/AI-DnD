#!/bin/bash
################################################################################
# D&D Narrative Theater - Startup Script
# Starts all three required servers for the AI-powered adventure system
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                                                               ║${NC}"
echo -e "${MAGENTA}║       🎭  D&D NARRATIVE THEATER - STARTUP SCRIPT  🎲         ║${NC}"
echo -e "${MAGENTA}║                                                               ║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for server to be ready
wait_for_server() {
    local port=$1
    local name=$2
    local max_attempts=30
    local attempt=0

    echo -e "${YELLOW}⏳ Waiting for $name to start...${NC}"

    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:$port/health >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $name is ready!${NC}"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done

    echo -e "${RED}❌ $name failed to start within 30 seconds${NC}"
    return 1
}

# Check if .env file exists
echo -e "${BLUE}🔍 Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ ERROR: .env file not found!${NC}"
    echo -e "${YELLOW}Please create a .env file with the following variables:${NC}"
    echo ""
    echo "GEMINI_API_KEY=your_gemini_api_key_here"
    echo "PIXELLAB_API_KEY=your_pixellab_api_key_here"
    echo ""
    exit 1
fi

# Check for required API keys
source .env
if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}❌ ERROR: GEMINI_API_KEY not set in .env${NC}"
    exit 1
fi

if [ -z "$PIXELLAB_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  WARNING: PIXELLAB_API_KEY not set in .env${NC}"
    echo -e "${YELLOW}   Pixel art sprites will not work, but other features will.${NC}"
fi

echo -e "${GREEN}✅ Environment configuration OK${NC}"
echo ""

# Check if servers are already running
echo -e "${BLUE}🔍 Checking for existing servers...${NC}"

SERVERS_RUNNING=0

if check_port 5000; then
    echo -e "${YELLOW}⚠️  Port 5000 (Nano Banana) is already in use${NC}"
    SERVERS_RUNNING=1
fi

if check_port 5001; then
    echo -e "${YELLOW}⚠️  Port 5001 (PixelLab Bridge) is already in use${NC}"
    SERVERS_RUNNING=1
fi

if check_port 5002; then
    echo -e "${YELLOW}⚠️  Port 5002 (Narrative Server) is already in use${NC}"
    SERVERS_RUNNING=1
fi

if [ $SERVERS_RUNNING -eq 1 ]; then
    echo ""
    echo -e "${YELLOW}Some servers are already running. Options:${NC}"
    echo -e "  1) Stop existing servers and restart (recommended)"
    echo -e "  2) Keep existing servers running"
    echo -e "  3) Exit"
    echo ""
    read -p "Choose an option (1-3): " choice

    case $choice in
        1)
            echo -e "${BLUE}🛑 Stopping existing servers...${NC}"
            pkill -f nano_banana_server.py 2>/dev/null || true
            pkill -f pixellab_bridge_server.py 2>/dev/null || true
            pkill -f dnd_narrative_server.py 2>/dev/null || true
            sleep 2
            echo -e "${GREEN}✅ Existing servers stopped${NC}"
            ;;
        2)
            echo -e "${GREEN}✅ Keeping existing servers${NC}"
            echo ""
            echo -e "${CYAN}🎮 Open in browser: file://${SCRIPT_DIR}/dnd-narrative-theater.html${NC}"
            exit 0
            ;;
        3)
            echo -e "${BLUE}👋 Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid option${NC}"
            exit 1
            ;;
    esac
fi

echo ""
echo -e "${BLUE}🚀 Starting servers...${NC}"
echo ""

# Start Nano Banana Server (Port 5000)
echo -e "${CYAN}[1/3] Starting Nano Banana Server (Gemini Image Generation)...${NC}"
python3 nano_banana_server.py > logs/nano_banana.log 2>&1 &
NANO_PID=$!
echo -e "${GREEN}✅ Nano Banana started (PID: $NANO_PID)${NC}"

# Wait for Nano Banana to be ready
wait_for_server 5000 "Nano Banana Server"

# Start PixelLab Bridge Server (Port 5001)
echo ""
echo -e "${CYAN}[2/3] Starting PixelLab Bridge Server (Pixel Art Sprites)...${NC}"
python3 pixellab_bridge_server.py > logs/pixellab_bridge.log 2>&1 &
PIXELLAB_PID=$!
echo -e "${GREEN}✅ PixelLab Bridge started (PID: $PIXELLAB_PID)${NC}"

# Wait for PixelLab to be ready
wait_for_server 5001 "PixelLab Bridge Server"

# Start Narrative Server (Port 5002)
echo ""
echo -e "${CYAN}[3/3] Starting D&D Narrative Server (Adventure Orchestration)...${NC}"
python3 dnd_narrative_server.py > logs/narrative_server.log 2>&1 &
NARRATIVE_PID=$!
echo -e "${GREEN}✅ Narrative Server started (PID: $NARRATIVE_PID)${NC}"

# Wait for Narrative Server to be ready
wait_for_server 5002 "D&D Narrative Server"

# Save PIDs to file for shutdown script
echo "$NANO_PID" > .narrative_theater_pids
echo "$PIXELLAB_PID" >> .narrative_theater_pids
echo "$NARRATIVE_PID" >> .narrative_theater_pids

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║          🎉  ALL SYSTEMS OPERATIONAL!  🎉                    ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${MAGENTA}📊 Server Status:${NC}"
echo -e "  ${GREEN}✅${NC} Port 5000: Nano Banana (Gemini Image Generation)"
echo -e "  ${GREEN}✅${NC} Port 5001: PixelLab Bridge (Pixel Art Sprites)"
echo -e "  ${GREEN}✅${NC} Port 5002: Narrative Server (Adventure Orchestration)"
echo ""

echo -e "${MAGENTA}🎮 Quick Start:${NC}"
echo -e "  1. Open this file in your browser:"
echo -e "     ${CYAN}file://${SCRIPT_DIR}/dnd-narrative-theater.html${NC}"
echo -e "  2. Enter a character name (e.g., 'Thorin')"
echo -e "  3. Click 'Start Adventure'"
echo -e "  4. Click '🎨 Generate Scene Art' for images"
echo ""

echo -e "${MAGENTA}📝 Useful Commands:${NC}"
echo -e "  View logs:      ${CYAN}tail -f logs/nano_banana.log${NC}"
echo -e "  Stop servers:   ${CYAN}./stop_theater.sh${NC}"
echo -e "  Check status:   ${CYAN}curl http://localhost:5002/health${NC}"
echo ""

echo -e "${YELLOW}💡 Tip: Press Ctrl+C to stop this script (servers will keep running)${NC}"
echo -e "${YELLOW}        Use ./stop_theater.sh to stop all servers${NC}"
echo ""

# Open in default browser (optional)
echo -e "${BLUE}🌐 Opening in browser...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "file://${SCRIPT_DIR}/dnd-narrative-theater.html"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open "file://${SCRIPT_DIR}/dnd-narrative-theater.html" 2>/dev/null || echo "Please open dnd-narrative-theater.html manually"
else
    echo -e "${YELLOW}Please open dnd-narrative-theater.html in your browser manually${NC}"
fi

echo ""
echo -e "${GREEN}🎭 Enjoy your AI-powered D&D adventures! 🎲${NC}"
echo ""

