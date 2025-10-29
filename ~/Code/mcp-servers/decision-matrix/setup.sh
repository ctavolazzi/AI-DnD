#!/bin/bash
"""
Setup script for Decision Matrix MCP Server
"""

set -e

echo "🧠 Decision Matrix MCP Server Setup"
echo "=================================="

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r decision_matrix_requirements.txt

# Make server executable
echo "🔧 Making server executable..."
chmod +x decision_matrix_mcp_server.py

# Run tests
echo "🧪 Running tests..."
python3 test_decision_matrix_mcp.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use this MCP server, add the following to your MCP configuration:"
echo ""
echo "{"
echo "  \"mcpServers\": {"
echo "    \"decision-matrix\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": [\"$(pwd)/decision_matrix_mcp_server.py\"],"
echo "      \"env\": {}"
echo "    }"
echo "  }"
echo "}"
echo ""
echo "For more information, see README.md"
