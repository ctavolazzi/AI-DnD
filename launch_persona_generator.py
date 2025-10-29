#!/usr/bin/env python3
"""
Persona Dossier Generator Launcher
Starts the backend server and opens the gallery in browser
"""

import subprocess
import webbrowser
import time
import requests
import sys
import os
from pathlib import Path

def check_nano_banana():
    """Check if Nano Banana is running"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_nano_banana():
    """Start Nano Banana server if not running"""
    print("🔍 Checking Nano Banana server...")

    if check_nano_banana():
        print("✅ Nano Banana is already running")
        return True

    print("🚀 Starting Nano Banana server...")
    try:
        # Try to start Nano Banana
        nano_banana_process = subprocess.Popen(
            ['python3', 'nano_banana_server.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait a bit for it to start
        time.sleep(3)

        if check_nano_banana():
            print("✅ Nano Banana started successfully")
            return True
        else:
            print("❌ Failed to start Nano Banana")
            return False

    except Exception as e:
        print(f"❌ Error starting Nano Banana: {e}")
        return False

def start_backend_server():
    """Start the Flask backend server"""
    print("🚀 Starting Persona Dossier backend server...")

    try:
        # Start the Flask server
        server_process = subprocess.Popen([
            sys.executable, 'persona_dossier_server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait for server to start
        time.sleep(2)

        # Check if server is running
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=5)
            if response.status_code == 200:
                print("✅ Backend server started successfully")
                return server_process
            else:
                print("❌ Backend server failed to start")
                return None
        except:
            print("❌ Backend server not responding")
            return None

    except Exception as e:
        print(f"❌ Error starting backend server: {e}")
        return None

def open_gallery():
    """Open the gallery in browser"""
    print("🌐 Opening gallery in browser...")

    gallery_path = Path(__file__).parent / 'persona_dossier_gallery.html'
    gallery_url = f"file://{gallery_path.absolute()}"

    try:
        webbrowser.open(gallery_url)
        print("✅ Gallery opened in browser")
        return True
    except Exception as e:
        print(f"❌ Error opening browser: {e}")
        return False

def main():
    """Main launcher function"""
    print("🎭 Persona Dossier Generator Launcher")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('nano_banana_server.py'):
        print("❌ Error: nano_banana_server.py not found")
        print("Please run this script from the AI-DnD project directory")
        return 1

    # Start Nano Banana
    if not start_nano_banana():
        print("⚠️  Warning: Nano Banana not available. Images will be placeholders.")

    # Start backend server
    server_process = start_backend_server()
    if not server_process:
        print("❌ Failed to start backend server")
        return 1

    # Open gallery
    if not open_gallery():
        print("⚠️  Could not open browser automatically")
        print(f"Please open: {Path(__file__).parent / 'persona_dossier_gallery.html'}")

    print("\n🎉 Persona Dossier Generator is ready!")
    print("=" * 50)
    print("📋 Instructions:")
    print("1. Configure your settings in the web interface")
    print("2. Click 'Generate Persona Dossier'")
    print("3. Watch the progress animation")
    print("4. Browse the generated images in the gallery")
    print("\n🛑 Press Ctrl+C to stop the server")

    try:
        # Keep the server running
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        server_process.terminate()
        print("✅ Server stopped")

    return 0

if __name__ == '__main__':
    sys.exit(main())
