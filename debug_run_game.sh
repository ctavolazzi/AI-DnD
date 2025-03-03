#!/bin/bash
# Run the game with debug options and analyze any errors

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# Print a section header
print_header() {
    echo -e "\n${BOLD}${BLUE}=== $1 ===${RESET}\n"
}

# Print a success message
print_success() {
    echo -e "${GREEN}✅ $1${RESET}"
}

# Print an error message
print_error() {
    echo -e "${RED}❌ $1${RESET}"
}

# Print a warning message
print_warning() {
    echo -e "${YELLOW}⚠️ $1${RESET}"
}

# Print an info message
print_info() {
    echo -e "${CYAN}ℹ️ $1${RESET}"
}

# Create logs directory if it doesn't exist
mkdir -p logs
print_info "Logs directory ensured at: logs/"

# Clear previous log files if they exist
if ls logs/ai_dnd_*.log &> /dev/null; then
    print_info "Clearing previous log files..."
    rm logs/ai_dnd_*.log
fi

# Print start message
print_header "AI-DnD Debug Run"
print_info "Starting debug run with the following configuration:"
echo -e "  ${MAGENTA}Vault:${RESET} character-journal-test-vault"
echo -e "  ${MAGENTA}Turns:${RESET} 5"
echo -e "  ${MAGENTA}Model:${RESET} mistral"

# Run the game with specified options
print_header "Running Game"
echo -e "${BOLD}Game output:${RESET}"
echo -e "${YELLOW}---------------------------------------------${RESET}"
python3 main.py --vault=character-journal-test-vault --turns=5 --model=mistral --verbose
GAME_EXIT_CODE=$?
echo -e "${YELLOW}---------------------------------------------${RESET}"

# Check if the game exited with an error code
if [ $GAME_EXIT_CODE -ne 0 ]; then
    print_error "Game exited with error code: $GAME_EXIT_CODE"
else
    print_success "Game exited with success code: $GAME_EXIT_CODE"
fi

# Check if there were errors in the logs directory
if ls logs/ai_dnd_errors_*.log &> /dev/null; then
    ERROR_COUNT=$(grep -c "ERROR" logs/ai_dnd_errors_*.log)
    print_warning "Detected $ERROR_COUNT errors in log files"

    print_header "Error Analysis"
    # Run the error analyzer
    python3 analyze_errors.py --log-dir=logs --detailed --most-recent=5

    print_info "To see full error details, run: ./analyze_errors.py --log-dir=logs --detailed"
else
    print_success "No errors detected in the logs directory"
fi

# Check for specific issues
print_header "Checking for Common Issues"

# Check for location issues
if grep -q "location" logs/ai_dnd_*.log 2>/dev/null; then
    LOCATION_ISSUES=$(grep -i "location" logs/ai_dnd_*.log | grep -i "error\|warn\|fail" | wc -l)
    if [ $LOCATION_ISSUES -gt 0 ]; then
        print_warning "Detected $LOCATION_ISSUES potential issues with locations"
        echo "Sample issues:"
        grep -i "location" logs/ai_dnd_*.log | grep -i "error\|warn\|fail" | head -3
    else
        print_success "No location-related issues detected"
    fi
fi

# Check for character issues
if grep -q "character" logs/ai_dnd_*.log 2>/dev/null; then
    CHARACTER_ISSUES=$(grep -i "character" logs/ai_dnd_*.log | grep -i "error\|warn\|fail" | wc -l)
    if [ $CHARACTER_ISSUES -gt 0 ]; then
        print_warning "Detected $CHARACTER_ISSUES potential issues with characters"
        echo "Sample issues:"
        grep -i "character" logs/ai_dnd_*.log | grep -i "error\|warn\|fail" | head -3
    else
        print_success "No character-related issues detected"
    fi
fi

print_header "Debug Run Complete"
print_info "Check the logs directory for detailed logs"
print_info "Run './analyze_errors.py --help' for more analysis options"