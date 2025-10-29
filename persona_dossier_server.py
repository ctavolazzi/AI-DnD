#!/usr/bin/env python3
"""
Persona Dossier Backend Server
Handles API calls for persona generation and image creation
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import asyncio
import aiohttp
import json
import os
import base64
from datetime import datetime
import logging
from simple_persona_generator import SimplePersonaGenerator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Global variable to track generation status
generation_status = {
    'is_generating': False,
    'progress': 0,
    'current_task': '',
    'current_image': 0,
    'total_images': 0,
    'persona_data': None,
    'images': [],
    'error': None
}

@app.route('/api/generate-persona', methods=['POST'])
async def generate_persona():
    """Generate a persona dossier with AI images"""
    global generation_status

    if generation_status['is_generating']:
        return jsonify({'error': 'Generation already in progress'}), 400

    try:
        data = request.get_json()
        num_images = data.get('numImages', 10)
        image_quality = data.get('imageQuality', 'balanced')
        persona_type = data.get('personaType', 'random')

        # Reset status
        generation_status.update({
            'is_generating': True,
            'progress': 0,
            'current_task': 'Initializing...',
            'current_image': 0,
            'total_images': num_images,
            'persona_data': None,
            'images': [],
            'error': None
        })

        # Start generation in background
        asyncio.create_task(generate_persona_background(num_images, image_quality, persona_type))

        return jsonify({'status': 'started', 'message': 'Generation started'})

    except Exception as e:
        logger.error(f"Error starting generation: {e}")
        generation_status['error'] = str(e)
        generation_status['is_generating'] = False
        return jsonify({'error': str(e)}), 500

async def generate_persona_background(num_images, image_quality, persona_type):
    """Background task to generate persona dossier"""
    global generation_status

    try:
        generator = SimplePersonaGenerator()

        # Step 1: Generate random person
        generation_status['current_task'] = 'Fetching random person data...'
        generation_status['progress'] = 10

        person_data = await generator.generate_random_person()
        generation_status['persona_data'] = person_data

        # Step 2: Generate images
        generation_status['current_task'] = 'Generating placeholder images...'
        generation_status['progress'] = 20

        images = []
        for i, scenario in enumerate(generator.image_scenarios[:num_images]):
            generation_status['current_image'] = i + 1
            generation_status['current_task'] = f'Generating image {i + 1}/{num_images}: {scenario}'
            generation_status['progress'] = 20 + (i / num_images) * 70

            image_path = generator.generate_placeholder_image(person_data, scenario, i)
            images.append({
                'path': image_path,
                'scenario': scenario,
                'index': i + 1
            })

            # Small delay to show progress
            await asyncio.sleep(0.5)

        # Step 3: Create dossier
        generation_status['current_task'] = 'Creating dossier...'
        generation_status['progress'] = 95

        dossier = {
            'person': person_data,
            'images': images,
            'generated_at': datetime.now().isoformat(),
            'total_images': len(images),
            'success_rate': len(images) / num_images * 100
        }

        # Save dossier
        dossier_file = f"persona_dossiers/{person_data['first_name'].lower()}_{person_data['last_name'].lower()}_dossier.json"
        os.makedirs("persona_dossiers", exist_ok=True)

        with open(dossier_file, 'w') as f:
            json.dump(dossier, f, indent=2)

        generation_status['images'] = images
        generation_status['progress'] = 100
        generation_status['current_task'] = 'Complete!'

    except Exception as e:
        logger.error(f"Error in background generation: {e}")
        generation_status['error'] = str(e)
    finally:
        generation_status['is_generating'] = False

@app.route('/api/generation-status', methods=['GET'])
def get_generation_status():
    """Get current generation status"""
    return jsonify(generation_status)

@app.route('/api/persona-image/<path:image_path>')
def get_persona_image(image_path):
    """Serve persona images"""
    try:
        return send_file(image_path)
    except Exception as e:
        logger.error(f"Error serving image {image_path}: {e}")
        return jsonify({'error': 'Image not found'}), 404

@app.route('/api/dossiers', methods=['GET'])
def list_dossiers():
    """List all generated dossiers"""
    try:
        dossiers = []
        if os.path.exists('persona_dossiers'):
            for filename in os.listdir('persona_dossiers'):
                if filename.endswith('.json'):
                    with open(f'persona_dossiers/{filename}', 'r') as f:
                        dossier = json.load(f)
                        dossiers.append({
                            'filename': filename,
                            'person_name': dossier['person']['name'],
                            'generated_at': dossier['generated_at'],
                            'total_images': dossier['total_images']
                        })

        return jsonify({'dossiers': dossiers})
    except Exception as e:
        logger.error(f"Error listing dossiers: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dossier/<filename>')
def get_dossier(filename):
    """Get a specific dossier"""
    try:
        dossier_path = f'persona_dossiers/{filename}'
        if os.path.exists(dossier_path):
            with open(dossier_path, 'r') as f:
                dossier = json.load(f)
            return jsonify(dossier)
        else:
            return jsonify({'error': 'Dossier not found'}), 404
    except Exception as e:
        logger.error(f"Error getting dossier {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'nano_banana_available': check_nano_banana_availability()
    })

def check_nano_banana_availability():
    """Check if Nano Banana API is available"""
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == '__main__':
    print("🎭 Persona Dossier Backend Server")
    print("=" * 50)
    print("Starting server on http://localhost:5002")
    print("Make sure Nano Banana is running on http://localhost:8000")
    print("Open persona_dossier_gallery.html in your browser")

    app.run(host='0.0.0.0', port=5002, debug=True)
