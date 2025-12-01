#!/usr/bin/env python3
"""
Simple PixelLab API Test
Test the basic API connection and response structure
"""

import pixellab
import os
import json

def test_api():
    """Test basic API functionality."""
    print("🎨 PixelLab API Test")
    print("=" * 40)

    # Initialize client
    API_KEY = os.getenv("PIXELLAB_API_KEY")
    if not API_KEY:
        print("❌ Error: PIXELLAB_API_KEY environment variable not set")
        print("Please set your API key: export PIXELLAB_API_KEY=your_key_here")
        return
    client = pixellab.Client(secret=API_KEY)

    try:
        # Test balance endpoint
        print("Testing balance endpoint...")
        balance_response = client.get_balance()
        print(f"Balance response type: {type(balance_response)}")
        print(f"Balance response: {balance_response}")

        # Try to access different attributes
        if hasattr(balance_response, 'credits'):
            print(f"Credits: {balance_response.credits}")
        if hasattr(balance_response, 'remaining_credits'):
            print(f"Remaining credits: {balance_response.remaining_credits}")
        if hasattr(balance_response, 'data'):
            print(f"Data: {balance_response.data}")

        # Test character generation
        print("\nTesting character generation...")
        character_response = client.generate_character(
            description="simple wizard",
            image_size=pixellab.models.ImageSize(width=64, height=64)
        )
        print(f"Character response type: {type(character_response)}")
        print(f"Character response: {character_response}")

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
