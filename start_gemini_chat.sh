#!/bin/bash

# Gemini Chat Launcher
# Quick script to open the Gemini chat interface

echo "🚀 Opening Gemini Chat Interface..."
echo ""
echo "📖 Quick Setup:"
echo "   1. Get your API key: https://aistudio.google.com/app/apikey"
echo "   2. Paste it in the input field"
echo "   3. Click 'Connect'"
echo "   4. Start chatting!"
echo ""

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open gemini-chat.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open gemini-chat.html
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    # Windows
    start gemini-chat.html
else
    echo "❌ Could not detect OS. Please open gemini-chat.html manually."
fi

