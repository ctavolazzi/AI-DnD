#!/bin/bash
################################################################################
# D&D Narrative Theater - Shutdown Script
# Stops all running servers gracefully
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}║                                                               ║${NC}"
echo -e "${MAGENTA}║       🎭  D&D NARRATIVE THEATER - SHUTDOWN SCRIPT  🛑        ║${NC}"
echo -e "${MAGENTA}║                                                               ║${NC}"
echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

SERVERS_FOUND=0

# Check if PID file exists
if [ -f .narrative_theater_pids ]; then
    echo -e "${BLUE}🔍 Found PID file, stopping servers by PID...${NC}"

    while IFS= read -r pid; do
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⏹️  Stopping process $pid...${NC}"
            kill "$pid" 2>/dev/null || true
            SERVERS_FOUND=1
        fi
    done < .narrative_theater_pids

    rm -f .narrative_theater_pids
    sleep 2
fi

# Also check by process name (backup method)
echo -e "${BLUE}🔍 Checking for running servers by name...${NC}"

if pgrep -f "nano_banana_server.py" > /dev/null; then
    echo -e "${YELLOW}⏹️  Stopping Nano Banana Server...${NC}"
    pkill -f "nano_banana_server.py"
    SERVERS_FOUND=1
fi

if pgrep -f "pixellab_bridge_server.py" > /dev/null; then
    echo -e "${YELLOW}⏹️  Stopping PixelLab Bridge Server...${NC}"
    pkill -f "pixellab_bridge_server.py"
    SERVERS_FOUND=1
fi

if pgrep -f "dnd_narrative_server.py" > /dev/null; then
    echo -e "${YELLOW}⏹️  Stopping D&D Narrative Server...${NC}"
    pkill -f "dnd_narrative_server.py"
    SERVERS_FOUND=1
fi

# Wait a moment for processes to terminate
sleep 2

# Verify all servers are stopped
echo ""
echo -e "${BLUE}🔍 Verifying shutdown...${NC}"

ALL_STOPPED=1

if pgrep -f "nano_banana_server.py" > /dev/null; then
    echo -e "${RED}❌ Nano Banana Server still running${NC}"
    ALL_STOPPED=0
fi

if pgrep -f "pixellab_bridge_server.py" > /dev/null; then
    echo -e "${RED}❌ PixelLab Bridge Server still running${NC}"
    ALL_STOPPED=0
fi

if pgrep -f "dnd_narrative_server.py" > /dev/null; then
    echo -e "${RED}❌ D&D Narrative Server still running${NC}"
    ALL_STOPPED=0
fi

echo ""

if [ $SERVERS_FOUND -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No running servers found${NC}"
    echo -e "${BLUE}All servers were already stopped${NC}"
elif [ $ALL_STOPPED -eq 1 ]; then
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}║          ✅  ALL SERVERS STOPPED SUCCESSFULLY  ✅            ║${NC}"
    echo -e "${GREEN}║                                                               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
else
    echo -e "${YELLOW}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}║                                                               ║${NC}"
    echo -e "${YELLOW}║      ⚠️  SOME SERVERS COULD NOT BE STOPPED  ⚠️             ║${NC}"
    echo -e "${YELLOW}║                                                               ║${NC}"
    echo -e "${YELLOW}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Try force killing with:${NC}"
    echo -e "  ${CYAN}pkill -9 -f nano_banana_server.py${NC}"
    echo -e "  ${CYAN}pkill -9 -f pixellab_bridge_server.py${NC}"
    echo -e "  ${CYAN}pkill -9 -f dnd_narrative_server.py${NC}"
fi

echo ""

