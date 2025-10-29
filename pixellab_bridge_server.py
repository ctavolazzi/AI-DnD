#!/usr/bin/env python3
"""
PixelLab Bridge Server
A simple Flask server that bridges browser requests to PixelLab MCP server
"""

import os
import base64
from io import BytesIO
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import pixellab

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configuration
PIXELLAB_API_KEY = os.getenv('PIXELLAB_API_KEY')
if not PIXELLAB_API_KEY:
    print("WARNING: PIXELLAB_API_KEY not found in environment variables!")
    print("Please set your PixelLab API key.")

# Initialize PixelLab client
client = None
if PIXELLAB_API_KEY:
    client = pixellab.Client(secret=PIXELLAB_API_KEY)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(PIXELLAB_API_KEY),
        'client_initialized': bool(client)
    })

@app.route('/generate-sprite', methods=['POST'])
def generate_sprite():
    """
    Generate a pixel art sprite using PixelLab.

    Request body:
    {
        "prompt": "fantasy knight with sword",
        "width": 64,
        "height": 64,
        "seed": null,
        "detail": "medium detail",
        "outline": "single color black outline",
        "shading": "basic shading",
        "no_background": false
    }

    Response:
    {
        "success": true,
        "image": "base64_encoded_image_data",
        "generation_time": 2.5
    }
    """
    if not client:
        return jsonify({
            'error': 'PixelLab client not initialized. Check PIXELLAB_API_KEY.'
        }), 500

    try:
        # Parse request
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({'error': 'Missing required field: prompt'}), 400

        prompt = data['prompt']
        width = data.get('width', 64)
        height = data.get('height', 64)
        seed = data.get('seed', None)
        detail = data.get('detail', 'medium detail')
        outline = data.get('outline', 'single color black outline')
        shading = data.get('shading', 'basic shading')
        no_background = data.get('no_background', False)

        print(f"🎨 Generating sprite: {prompt} ({width}x{height})")

        # Generate sprite using PixelLab
        response = client.generate_image_pixflux(
            description=prompt,
            image_size={"width": width, "height": height},
            seed=seed,
            detail=detail,
            outline=outline,
            shading=shading,
            no_background=no_background
        )

        # Get the PIL image
        pil_image = response.image.pil_image()

        # Convert to base64
        buffered = BytesIO()
        pil_image.save(buffered, format='PNG')
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        print(f"✅ Sprite generated successfully")

        return jsonify({
            'success': True,
            'image': img_base64,
            'width': width,
            'height': height
        })

    except Exception as e:
        print(f"❌ Error generating sprite: {str(e)}")
        return jsonify({
            'error': f'Sprite generation failed: {str(e)}'
        }), 500

@app.route('/get-balance', methods=['GET'])
def get_balance():
    """Check PixelLab API credit balance"""
    if not client:
        return jsonify({
            'error': 'PixelLab client not initialized. Check PIXELLAB_API_KEY.'
        }), 500

    try:
        balance = client.get_balance()
        return jsonify({
            'success': True,
            'balance': {
                'usd': balance.usd,
                'type': balance.type
            }
        })
    except Exception as e:
        return jsonify({
            'error': f'Failed to get balance: {str(e)}'
        }), 500

if __name__ == '__main__':
    if not PIXELLAB_API_KEY:
        print("\n" + "="*60)
        print("ERROR: PIXELLAB_API_KEY not configured!")
        print("="*60)
        print("\nTo configure:")
        print("1. Create a .env file in this directory")
        print("2. Add: PIXELLAB_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://www.pixellab.ai")
        print("\n" + "="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("🎨 PixelLab Bridge Server")
        print("="*60)
        print(f"✓ API Key configured")
        print(f"✓ Running on http://localhost:5001")
        print("\nEndpoints:")
        print("  GET  /health          - Health check")
        print("  POST /generate-sprite - Generate pixel art sprite")
        print("  GET  /get-balance     - Check API balance")
        print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5001)

