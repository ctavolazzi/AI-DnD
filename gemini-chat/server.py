#!/usr/bin/env python3
"""
Simple HTTP server for Gemini Chat Interface
Automatically opens the browser when started
"""

import http.server
import socketserver
import webbrowser
import os
from threading import Timer

PORT = 8000

def open_browser():
    """Open the browser after a short delay"""
    webbrowser.open(f'http://localhost:{PORT}')

# Change to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map.update({
    '.js': 'application/javascript',
})

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("=" * 60)
    print("🚀 Gemini Chat Interface Server")
    print("=" * 60)
    print(f"\n✨ Server running at: http://localhost:{PORT}")
    print(f"\n📖 Quick Setup:")
    print(f"   1. Get your API key: https://aistudio.google.com/app/apikey")
    print(f"   2. Paste it in the input field")
    print(f"   3. Click 'Connect'")
    print(f"   4. Start chatting!")
    print(f"\n🎨 Pro Tip: Try the different themes!")
    print(f"💡 Pro Tip: Open the console (F12) for advanced features!")
    print(f"\n⚠️  Press Ctrl+C to stop the server\n")
    print("=" * 60)

    # Open browser after 1 second
    Timer(1, open_browser).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
        httpd.shutdown()

