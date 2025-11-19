#!/usr/bin/env python3
"""
Simple HTTP server for serving test results
Run this to view test_results_viewer.html with live test log access
"""
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080

class TestResultsHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    # Change to project root directory
    os.chdir(Path(__file__).parent)

    with socketserver.TCPServer(("", PORT), TestResultsHandler) as httpd:
        print(f"🚀 Test Results Server running on http://localhost:{PORT}")
        print(f"📁 Serving files from: {os.getcwd()}")
        print(f"🌐 Open http://localhost:{PORT}/test_results_viewer.html in your browser")
        print(f"\n📝 To view test results:")
        print(f"   1. Run: python3 test_gemini_narrative.py 2>&1 | tee test_output.log")
        print(f"   2. Open: http://localhost:{PORT}/test_results_viewer.html")
        print(f"   3. Click '🌐 Load from Server' button")
        print(f"\nPress Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")

if __name__ == "__main__":
    main()

