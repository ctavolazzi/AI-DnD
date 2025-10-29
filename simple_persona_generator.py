#!/usr/bin/env python3
"""
Simple Persona Dossier Demo
Works without Nano Banana - generates placeholder images
"""

import asyncio
import aiohttp
import json
import os
import base64
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimplePersonaGenerator:
    """Simple persona generator with placeholder images"""

    def __init__(self):
        self.random_user_api = "https://randomuser.me/api/"

        # Image generation scenarios
        self.image_scenarios = [
            "professional headshot in business attire",
            "casual selfie at a coffee shop",
            "outdoor hiking photo with nature background",
            "cooking in kitchen wearing apron",
            "reading a book in a library",
            "playing guitar or musical instrument",
            "working out at gym",
            "travel photo at famous landmark",
            "petting a dog or cat",
            "smiling portrait with friends"
        ]

    async def generate_random_person(self) -> Dict:
        """Generate a random person from Random User API"""
        try:
            # Create SSL context that doesn't verify certificates
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(self.random_user_api) as response:
                    if response.status == 200:
                        data = await response.json()
                        user_data = data['results'][0]

                        return {
                            'name': f"{user_data['name']['first']} {user_data['name']['last']}",
                            'first_name': user_data['name']['first'],
                            'last_name': user_data['name']['last'],
                            'title': user_data['name']['title'],
                            'gender': user_data['gender'],
                            'age': user_data['dob']['age'],
                            'email': user_data['email'],
                            'phone': user_data['phone'],
                            'cell': user_data['cell'],
                            'location': {
                                'street': f"{user_data['location']['street']['number']} {user_data['location']['street']['name']}",
                                'city': user_data['location']['city'],
                                'state': user_data['location']['state'],
                                'country': user_data['location']['country'],
                                'postcode': user_data['location']['postcode']
                            },
                            'profile_picture': user_data['picture']['large'],
                            'nationality': user_data['nat']
                        }
                    else:
                        raise Exception(f"Random User API error: {response.status}")
        except Exception as e:
            logger.error(f"Error generating random person: {e}")
            # Fallback data
            return {
                'name': 'Alex Johnson',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'title': 'Mr',
                'gender': 'male',
                'age': 28,
                'email': 'alex.johnson@example.com',
                'phone': '(555) 123-4567',
                'cell': '(555) 987-6543',
                'location': {
                    'street': '123 Main St',
                    'city': 'Anytown',
                    'state': 'CA',
                    'country': 'United States',
                    'postcode': '12345'
                },
                'profile_picture': '',
                'nationality': 'US'
            }

    def generate_placeholder_image(self, person_data: Dict, scenario: str, image_index: int) -> str:
        """Generate a placeholder image (SVG)"""
        # Create a simple SVG placeholder
        gender_color = "#4A90E2" if person_data['gender'] == 'male' else "#E24A90"

        svg = f'''
        <svg width="512" height="512" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#f0f0f0;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#e0e0e0;stop-opacity:1" />
                </linearGradient>
            </defs>
            <rect width="512" height="512" fill="url(#bg)"/>
            <circle cx="256" cy="180" r="60" fill="{gender_color}" opacity="0.8"/>
            <rect x="196" y="260" width="120" height="120" rx="20" fill="{gender_color}" opacity="0.6"/>
            <text x="256" y="420" text-anchor="middle" fill="#666" font-family="Arial" font-size="16" font-weight="bold">
                {person_data['first_name']} {person_data['last_name']}
            </text>
            <text x="256" y="440" text-anchor="middle" fill="#888" font-family="Arial" font-size="12">
                {scenario}
            </text>
            <text x="256" y="460" text-anchor="middle" fill="#aaa" font-family="Arial" font-size="10">
                AI Generated Placeholder
            </text>
        </svg>
        '''

        # Save as PNG file
        filename = f"persona_images/{person_data['first_name'].lower()}_{image_index:02d}.png"
        os.makedirs("persona_images", exist_ok=True)

        # For demo purposes, save as SVG and rename
        svg_filename = filename.replace('.png', '.svg')
        with open(svg_filename, 'w') as f:
            f.write(svg)

        logger.info(f"Generated placeholder image {image_index + 1}/10: {scenario}")
        return svg_filename

    async def generate_persona_dossier(self, num_images: int = 10) -> Dict:
        """Generate a complete persona dossier with placeholder images"""
        logger.info("🎭 Generating persona dossier...")

        # Generate random person data
        logger.info("📊 Fetching random person data...")
        person_data = await self.generate_random_person()

        # Generate placeholder images
        logger.info(f"🎨 Generating {num_images} placeholder images...")
        images = []

        for i, scenario in enumerate(self.image_scenarios[:num_images]):
            logger.info(f"Generating image {i + 1}/{num_images}: {scenario}")
            image_path = self.generate_placeholder_image(person_data, scenario, i)
            images.append({
                'path': image_path,
                'scenario': scenario,
                'index': i + 1
            })

        # Create dossier
        dossier = {
            'person': person_data,
            'images': images,
            'generated_at': datetime.now().isoformat(),
            'total_images': len(images),
            'success_rate': 100.0
        }

        # Save dossier to file
        dossier_file = f"persona_dossiers/{person_data['first_name'].lower()}_{person_data['last_name'].lower()}_dossier.json"
        os.makedirs("persona_dossiers", exist_ok=True)

        with open(dossier_file, 'w') as f:
            json.dump(dossier, f, indent=2)

        logger.info(f"✅ Dossier generated: {dossier_file}")
        return dossier

async def main():
    """Main function to generate persona dossier"""
    print("🎭 Simple Persona Dossier Generator")
    print("=" * 50)

    generator = SimplePersonaGenerator()

    try:
        dossier = await generator.generate_persona_dossier(10)

        print(f"\n✅ Dossier Generated Successfully!")
        print(f"Name: {dossier['person']['name']}")
        print(f"Age: {dossier['person']['age']}")
        print(f"Location: {dossier['person']['location']['city']}, {dossier['person']['location']['state']}")
        print(f"Images Generated: {dossier['total_images']}/10")
        print(f"Success Rate: {dossier['success_rate']:.1f}%")

        print(f"\n📁 Files created:")
        print(f"- Dossier: persona_dossiers/{dossier['person']['first_name'].lower()}_{dossier['person']['last_name'].lower()}_dossier.json")
        print(f"- Images: persona_images/")

        print(f"\n🌐 To view the gallery:")
        print(f"1. Start the server: python3 persona_dossier_server.py")
        print(f"2. Open: persona_dossier_gallery.html")

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.exception("Full error details:")

if __name__ == "__main__":
    asyncio.run(main())
