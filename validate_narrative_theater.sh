#!/bin/bash

# Narrative Theater Validation Script
# Checks all components are in place

echo "🎭 Validating Narrative Theater Installation..."
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
        ((PASSED++))
    else
        echo -e "${RED}❌${NC} $1 (missing)"
        ((FAILED++))
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 (executable)"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️${NC} $1 (not executable - run: chmod +x $1)"
        ((FAILED++))
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✅${NC} $1/"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️${NC} $1/ (will be created on first run)"
    fi
}

echo "📁 Core Files:"
check_file "dnd_narrative_server.py"
check_file "dnd-narrative-theater.html"
check_file "narrative_theater_requirements.txt"

echo ""
echo "🔧 Scripts:"
check_executable "start_narrative_theater.sh"
check_executable "stop_narrative_theater.sh"

echo ""
echo "📖 Documentation:"
check_file "NARRATIVE_THEATER_README.md"
check_file "QUICK_START_GUIDE.md"
check_file "NARRATIVE_THEATER_IMPLEMENTATION_COMPLETE.md"

echo ""
echo "📂 Directories:"
check_dir "logs"

echo ""
echo "🔗 Dependencies (existing files):"
check_file "dnd_game.py"
check_file "narrative_engine.py"
check_file "nano_banana_server.py"
check_file "pixellab_bridge_server.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ VALIDATION PASSED!${NC}"
    echo "All components are in place."
    echo ""
    echo "Next steps:"
    echo "1. Set API keys: export PIXELLAB_API_KEY=... GEMINI_API_KEY=..."
    echo "2. Start servers: ./start_narrative_theater.sh"
    echo "3. Open: dnd-narrative-theater.html"
else
    echo -e "${YELLOW}⚠️ VALIDATION INCOMPLETE${NC}"
    echo "Some components need attention (see above)."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Tests passed: $PASSED"
echo "Tests failed: $FAILED"

