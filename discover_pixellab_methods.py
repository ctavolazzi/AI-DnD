#!/usr/bin/env python3
"""
PixelLab API Method Discovery
Discover what methods are available on the client
"""

import pixellab
import os
import inspect

def discover_methods():
    """Discover available methods on the PixelLab client."""
    print("🔍 PixelLab API Method Discovery")
    print("=" * 50)

    # Initialize client
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("Please set your API key: export PIXELLAB_API_KEY=your_key_here")
        return
    client = pixellab.Client(secret=API_KEY)

    print(f"Client type: {type(client)}")
    print(f"Client class: {client.__class__}")

    # Get all methods
    methods = [method for method in dir(client) if not method.startswith('_')]
    print(f"\nAvailable methods ({len(methods)}):")
    for method in methods:
        print(f"  - {method}")

    # Check balance response structure
    print(f"\nBalance response structure:")
    balance = client.get_balance()
    print(f"  Type: {type(balance)}")
    print(f"  Attributes: {[attr for attr in dir(balance) if not attr.startswith('_')]}")
    print(f"  Values: {balance}")

    # Try to find character generation methods
    character_methods = [method for method in methods if 'character' in method.lower()]
    print(f"\nCharacter-related methods: {character_methods}")

    # Try to find generation methods
    generation_methods = [method for method in methods if 'generate' in method.lower()]
    print(f"Generation-related methods: {generation_methods}")

    # Try to find animation methods
    animation_methods = [method for method in methods if 'animate' in method.lower()]
    print(f"Animation-related methods: {animation_methods}")

if __name__ == "__main__":
    discover_methods()
