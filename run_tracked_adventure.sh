#!/bin/bash

# D&D Narrative Theater - Tracked Adventure Test Runner
# Coordinates backend monitoring and frontend tracking for comprehensive analysis

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     🎭  D&D NARRATIVE THEATER - TRACKED ADVENTURE  📊        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if servers are running
print_status "Checking server status..."

check_server() {
    local port=$1
    local name=$2

    if curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        print_success "$name server is running on port $port"
        return 0
    else
        print_warning "$name server is NOT running on port $port"
        return 1
    fi
}

SERVERS_OK=true

if ! check_server 5000 "Nano Banana"; then
    SERVERS_OK=false
fi

if ! check_server 5001 "PixelLab Bridge"; then
    SERVERS_OK=false
fi

if ! check_server 5002 "Narrative"; then
    SERVERS_OK=false
fi

if [ "$SERVERS_OK" = false ]; then
    echo ""
    print_error "Some servers are not running!"
    print_status "Would you like to start them? [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        print_status "Starting servers..."
        ./start_theater.sh
        echo ""
        print_success "Servers started!"
        sleep 2
    else
        print_error "Cannot run tracked adventure without servers"
        exit 1
    fi
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                  TRACKING OPTIONS                             ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Choose tracking mode:"
echo "  1) Browser-only tracking (Live UI + automated frontend tracking)"
echo "  2) Backend-only monitoring (Terminal logs + server metrics)"
echo "  3) Full tracking (Both browser and backend - RECOMMENDED)"
echo ""
read -p "Enter choice [1-3] (default: 3): " tracking_choice
tracking_choice=${tracking_choice:-3}

echo ""
print_status "Preparing tracking environment..."

# Create tracking session directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
SESSION_DIR="tracking_sessions/session_${TIMESTAMP}"
mkdir -p "$SESSION_DIR"
print_success "Session directory created: $SESSION_DIR"

# Start appropriate tracking
case $tracking_choice in
    1)
        print_status "Starting browser-only tracking..."
        echo ""
        print_success "Opening live adventure tracker in browser..."

        # Open the tracker
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "file://$SCRIPT_DIR/live-adventure-tracker.html"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "file://$SCRIPT_DIR/live-adventure-tracker.html"
        fi

        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        echo "📋 INSTRUCTIONS:"
        echo ""
        echo "  1. The Live Adventure Tracker has opened in your browser"
        echo "  2. Click '🚀 Start Tracked Adventure' button"
        echo "  3. Interact with the adventure in the embedded frame"
        echo "  4. Click '📊 Generate Full Report' when done"
        echo ""
        echo "  The tracker will automatically capture:"
        echo "    - All API calls and responses"
        echo "    - Image generation events"
        echo "    - Timing and performance metrics"
        echo "    - Complete timeline of events"
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        ;;

    2)
        print_status "Starting backend-only monitoring..."
        echo ""
        print_warning "Backend monitor will track server logs in real-time"
        print_status "Press Ctrl+C when adventure is complete to generate report"
        echo ""
        sleep 2

        # Run the Python monitor
        python3 monitor_adventure.py

        # Move generated reports to session directory
        mv adventure_analysis_*.md "$SESSION_DIR/" 2>/dev/null || true
        mv adventure_analysis_*.json "$SESSION_DIR/" 2>/dev/null || true
        ;;

    3)
        print_status "Starting FULL tracking (browser + backend)..."
        echo ""

        # Start backend monitor in background
        print_status "Starting backend monitor..."
        python3 monitor_adventure.py > "$SESSION_DIR/backend_monitor.log" 2>&1 &
        MONITOR_PID=$!
        echo "$MONITOR_PID" > "$SESSION_DIR/monitor.pid"
        print_success "Backend monitor running (PID: $MONITOR_PID)"

        # Open browser tracker
        print_status "Opening browser tracker..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "file://$SCRIPT_DIR/live-adventure-tracker.html"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "file://$SCRIPT_DIR/live-adventure-tracker.html"
        fi

        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
        echo "📋 FULL TRACKING ACTIVE:"
        echo ""
        echo "  🌐 FRONTEND: Live Adventure Tracker (browser)"
        echo "     - Click '🚀 Start Tracked Adventure'"
        echo "     - Click '📊 Generate Full Report' when done"
        echo ""
        echo "  🖥️  BACKEND: Monitor running (PID: $MONITOR_PID)"
        echo "     - Automatically tracking server logs"
        echo "     - Capturing all API calls and errors"
        echo ""
        echo "  When you're finished with the adventure:"
        echo "     1. Generate report in browser"
        echo "     2. Press Enter here to stop backend monitor"
        echo "     3. Complete analysis will be generated"
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo ""

        read -p "Press Enter when adventure is complete..."

        # Stop backend monitor
        print_status "Stopping backend monitor..."
        if [ -f "$SESSION_DIR/monitor.pid" ]; then
            kill $(cat "$SESSION_DIR/monitor.pid") 2>/dev/null || true
            rm "$SESSION_DIR/monitor.pid"
        fi

        # Move reports
        mv adventure_analysis_*.md "$SESSION_DIR/" 2>/dev/null || true
        mv adventure_analysis_*.json "$SESSION_DIR/" 2>/dev/null || true

        print_success "Backend monitor stopped"
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Generate summary if we have reports
if [ -d "$SESSION_DIR" ] && [ "$(ls -A $SESSION_DIR)" ]; then
    echo ""
    print_success "Tracking complete! Files saved to: $SESSION_DIR"
    echo ""
    print_status "Generated files:"
    ls -lh "$SESSION_DIR" | tail -n +2 | while read -r line; do
        echo "  📄 $line"
    done
    echo ""
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║               ✅  TRACKING SESSION COMPLETE  ✅               ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Offer to view reports
if [ -d "$SESSION_DIR" ] && [ -f "$SESSION_DIR"/*.md ]; then
    read -p "Would you like to view the analysis report now? [y/N] " view_report
    if [[ "$view_report" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        # Find the markdown file
        MD_FILE=$(ls "$SESSION_DIR"/*.md | head -n 1)
        if [ -n "$MD_FILE" ]; then
            echo ""
            echo "═══════════════════════════════════════════════════════════════"
            cat "$MD_FILE"
            echo "═══════════════════════════════════════════════════════════════"
        fi
    fi
fi

echo ""
print_success "Thank you for testing D&D Narrative Theater! 🎭🎲"
echo ""



