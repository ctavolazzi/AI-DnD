#!/usr/bin/env python3
"""
Nano Banana Image Generation Server
A Flask microservice that securely handles Gemini API image generation requests.
"""

import os
import base64
from io import BytesIO
from typing import Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
import time
from functools import wraps

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    print("WARNING: GEMINI_API_KEY not found in environment variables!")
    print("Please create a .env file with your API key.")

# Media resolution helpers
MEDIA_RESOLUTION_LEVELS = {
    "media_resolution_low",
    "media_resolution_medium",
    "media_resolution_high"
}


def normalize_media_resolution(value: Optional[str], default: str = "media_resolution_high") -> str:
    """Normalize user-provided media resolution values."""
    if not value:
        return default

    normalized = str(value).strip().lower()
    if not normalized.startswith("media_resolution_"):
        normalized = f"media_resolution_{normalized}"

    if normalized not in MEDIA_RESOLUTION_LEVELS:
        return default

    return normalized


DEFAULT_MEDIA_RESOLUTION = normalize_media_resolution(os.getenv("GEMINI_MEDIA_RESOLUTION"))

# Initialize Gemini client
client = None
if GEMINI_API_KEY:
    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options={"api_version": "v1alpha"}
    )

# Simple rate limiting (in-memory, not production-ready)
request_times = []
MAX_REQUESTS_PER_MINUTE = 10

def validate_custom_prompt(custom_prompt, item_name, description):
    """
    Validate custom prompt for item image generation.
    Returns error message if invalid, None if valid.
    """
    # Length check
    if len(custom_prompt) > 200:
        return "Custom prompt exceeds 200 character limit"

    if len(description) > 1000:
        return "Total prompt exceeds 1000 character limit"

    # Check for dangerous content
    dangerous_patterns = ['<script', 'javascript:', 'onerror', 'eval(', '<?php', '<iframe']
    for pattern in dangerous_patterns:
        if pattern in custom_prompt.lower() or pattern in description.lower():
            return "Invalid content detected in prompt"

    # Validate item name is in description (if item name provided)
    if item_name and item_name.lower() not in description.lower():
        return f"Prompt must contain item name: {item_name}"

    # Log for monitoring
    print(f"✓ Custom prompt validated: item='{item_name}', custom='{custom_prompt[:50]}...'")

    return None

def rate_limit(f):
    """Simple rate limiting decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        global request_times
        now = time.time()
        # Remove requests older than 1 minute
        request_times = [t for t in request_times if now - t < 60]

        if len(request_times) >= MAX_REQUESTS_PER_MINUTE:
            return jsonify({
                'error': 'Rate limit exceeded. Maximum 10 requests per minute.'
            }), 429

        request_times.append(now)
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'api_key_configured': bool(GEMINI_API_KEY),
        'client_initialized': bool(client)
    })

@app.route('/generate', methods=['POST'])
@app.route('/generate-image', methods=['POST'])
@rate_limit
def generate_image():
    """
    Generate an image using Gemini 2.5 Flash Image.

    Request body:
    {
        "prompt": "Description of the image to generate",
        "aspect_ratio": "16:9" (optional, default: "1:1"),
        "response_modalities": ["Text", "Image"] (optional)
    }

    Response:
    {
        "success": true,
        "image": "base64_encoded_image_data",
        "text": "optional text response",
        "generation_time": 2.5
    }
    """
    if not client:
        error_msg = 'Gemini API client not initialized. Check GEMINI_API_KEY.'
        print(f"❌ {error_msg}")
        return jsonify({'error': error_msg}), 500

    try:
        # Parse request
        data = request.get_json()
        if not data or 'prompt' not in data:
            print("❌ Missing prompt in request")
            return jsonify({'error': 'Missing required field: prompt'}), 400

        prompt = data['prompt']
        aspect_ratio = data.get('aspect_ratio', '1:1')
        response_modalities = data.get('response_modalities', ['Text', 'Image'])

        print(f"🎨 Generating image with prompt: {prompt[:100]}...")
        print(f"   Aspect ratio: {aspect_ratio}")

        # Validate aspect ratio
        valid_ratios = ['1:1', '2:3', '3:2', '3:4', '4:3', '4:5', '5:4', '9:16', '16:9', '21:9']
        if aspect_ratio not in valid_ratios:
            return jsonify({
                'error': f'Invalid aspect_ratio. Must be one of: {", ".join(valid_ratios)}'
            }), 400

        # Start timing
        start_time = time.time()

        # Generate image using Gemini 2.5 Flash Image Preview
        print("🔄 Calling Gemini API...")
        response = client.models.generate_content(
            model='gemini-2.5-flash-image-preview',
            contents=[prompt]
        )
        print(f"✅ Gemini responded in {time.time() - start_time:.2f}s")

        # Extract results
        result = {
            'success': True,
            'generation_time': round(time.time() - start_time, 2)
        }

        # Extract image and text from response
        has_image = False
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                result['text'] = part.text
                print(f"   Text received: {part.text[:50]}...")
            elif part.inline_data is not None:
                # Convert image to base64
                print(f"   Image data received: {len(part.inline_data.data)} bytes")
                image = Image.open(BytesIO(part.inline_data.data))
                buffered = BytesIO()
                image.save(buffered, format='PNG')
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                result['image'] = img_base64
                has_image = True
                print(f"   Base64 encoded: {len(img_base64)} chars")

        if not has_image and 'Image' in response_modalities:
            error_msg = 'Image generation failed. No image in response.'
            print(f"❌ {error_msg}")
            return jsonify({
                'error': error_msg,
                'success': False
            }), 500

        print(f"✅ Image generation successful!")
        return jsonify(result)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error generating image: {str(e)}")
        print(f"Traceback:\n{error_trace}")
        return jsonify({
            'error': f'Image generation failed: {str(e)}',
            'success': False
        }), 500

@app.route('/generate-scene', methods=['POST'])
@rate_limit
def generate_scene():
    """
    Generate or enhance an image using Gemini's image generation.

    Request body:
    {
        "description": "fantasy knight with sword and shield, cinematic lighting",
        "base_sprite": "base64_image_data" (optional - if provided, will enhance this image),
        "style": "photorealistic" (optional),
        "aspect_ratio": "1:1" (optional),
        "media_resolution": "high" (optional - low/high, default high)
    }
    """
    if not client:
        return jsonify({
            'error': 'Gemini API client not initialized. Check GEMINI_API_KEY.'
        }), 500

    try:
        data = request.get_json()
        if not data or 'description' not in data:
            return jsonify({'error': 'Missing required field: description'}), 400

        description = data['description']
        base_sprite = data.get('baseSprite')  # Base64 encoded sprite image
        style = data.get('style', 'photorealistic')
        requested_resolution = normalize_media_resolution(
            data.get('media_resolution'),
            default=DEFAULT_MEDIA_RESOLUTION
        )

        # Start timing
        start_time = time.time()

        # Build the prompt
        style_prompts = {
            'photorealistic': 'Transform this into a photorealistic, highly detailed image:',
            'fantasy_art': 'Transform this into detailed fantasy artwork:',
            'comic': 'Transform this into comic book style illustration:',
            'cyberpunk': 'Transform this into a cyberpunk style image:',
            'medieval': 'Transform this into a medieval fantasy style:',
        }

        style_prefix = style_prompts.get(style, style_prompts['photorealistic'])
        prompt = f"{style_prefix} {description}"

        # Prepare contents for Gemini
        contents = []
        generation_config = types.GenerateContentConfig(
            media_resolution={"level": requested_resolution}
        )

        # If base sprite provided, include it for image-to-image enhancement
        if base_sprite:
            # Remove data URL prefix if present
            if base_sprite.startswith('data:image'):
                base_sprite = base_sprite.split(',')[1]

            # Decode base64 to bytes
            image_bytes = base64.b64decode(base_sprite)

            contents.append(
                types.Part(
                    inline_data=types.Blob(
                        mime_type='image/png',
                        data=image_bytes
                    ),
                    media_resolution={"level": requested_resolution}
                )
            )

        # Add text prompt
        contents.append(prompt)

        # Generate image using Gemini 2.5 Flash Image Preview
        response = client.models.generate_content(
            model='gemini-2.5-flash-image-preview',
            contents=contents,
            config=generation_config
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                buffered = BytesIO()
                image.save(buffered, format='PNG')
                img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

                return jsonify({
                    'success': True,
                    'image': img_base64,
                    'generation_time': round(time.time() - start_time, 2),
                    'prompt': prompt
                })

        return jsonify({
            'error': 'No image data in response'
        }), 500

    except Exception as e:
        print(f"Error generating scene: {str(e)}")
        return jsonify({
            'error': f'Scene generation failed: {str(e)}'
        }), 500

def generate_image_internal(prompt, aspect_ratio='1:1'):
    """Internal helper for image generation using Gemini 2.5 Flash Image Preview"""
    start_time = time.time()

    # Generate image using Gemini's native image generation
    response = client.models.generate_content(
        model='gemini-2.5-flash-image-preview',
        contents=[prompt]
    )

    # Extract image from response
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            image = Image.open(BytesIO(part.inline_data.data))
            buffered = BytesIO()
            image.save(buffered, format='PNG')
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            return jsonify({
                'success': True,
                'image': img_base64,
                'generation_time': round(time.time() - start_time, 2),
                'prompt': prompt
            })

    raise Exception("No image data in response")

if __name__ == '__main__':
    if not GEMINI_API_KEY:
        print("\n" + "="*60)
        print("ERROR: GEMINI_API_KEY not configured!")
        print("="*60)
        print("\nTo configure:")
        print("1. Create a .env file in this directory")
        print("2. Add: GEMINI_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://ai.google.dev/")
        print("\n" + "="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("🍌 Nano Banana Image Generation Server")
        print("="*60)
        print(f"✓ API Key configured")
        print(f"✓ Running on http://localhost:5000")
        print(f"✓ Rate limit: {MAX_REQUESTS_PER_MINUTE} requests/minute")
        print("\nEndpoints:")
        print("  GET  /health          - Health check")
        print("  POST /generate-image  - Generate from prompt")
        print("  POST /generate-scene  - Generate D&D scene")
        print("="*60 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
