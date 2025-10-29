#!/bin/bash

# Stop all Narrative Theater servers

echo "🛑 Stopping Narrative Theater servers..."

# Read PIDs from file if it exists
if [ -f ".narrative_theater_pids" ]; then
    while read pid; do
        if ps -p $pid > /dev/null; then
            echo "  Stopping process $pid"
            kill $pid 2>/dev/null
        fi
    done < .narrative_theater_pids
    rm -f .narrative_theater_pids
fi

# Also kill by port
for port in 5000 5001 5002; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "  Stopping process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

echo "✅ All servers stopped"

