#!/usr/bin/env python3
"""
Persona Dossier Generator
Combines Random User API with Nano Banana to create fake personas with AI-generated images
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

class PersonaDossierGenerator:
    """Generates complete persona dossiers with AI images"""

    def __init__(self):
        self.random_user_api = "https://randomuser.me/api/"
        self.nano_banana_api = "http://localhost:8000"  # Adjust if different
        self.session = None

        # Image generation scenarios for different activities
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

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def generate_random_person(self) -> Dict:
        """Generate a random person from Random User API"""
        try:
            # Create SSL context that doesn't verify certificates
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            async with aiohttp.ClientSession(connector=connector) as temp_session:
                async with temp_session.get(self.random_user_api) as response:
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

    async def generate_ai_image(self, person_data: Dict, scenario: str, image_index: int) -> Optional[str]:
        """Generate an AI image using Nano Banana"""
        try:
            # Create a detailed prompt based on person data and scenario
            gender_desc = "man" if person_data['gender'] == 'male' else "woman"
            age_desc = f"in their {person_data['age']}s"

            prompt = f"A {gender_desc} {age_desc} {scenario}. High quality, realistic photo style. Natural lighting, detailed facial features."

            # Call Nano Banana API
            payload = {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted, unrealistic, cartoon, anime",
                "width": 512,
                "height": 512,
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            }

            async with self.session.post(
                f"{self.nano_banana_api}/generate",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if 'image' in result:
                        # Save image to file
                        image_data = base64.b64decode(result['image'])
                        filename = f"persona_images/{person_data['first_name'].lower()}_{image_index:02d}.png"
                        os.makedirs("persona_images", exist_ok=True)

                        with open(filename, 'wb') as f:
                            f.write(image_data)

                        logger.info(f"Generated image {image_index + 1}/10: {scenario}")
                        return filename
                    else:
                        logger.error(f"No image in response: {result}")
                        return None
                else:
                    logger.error(f"Nano Banana API error: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error generating AI image: {e}")
            return None

    async def generate_persona_dossier(self, num_images: int = 10) -> Dict:
        """Generate a complete persona dossier with images"""
        logger.info("🎭 Generating persona dossier...")

        # Generate random person data
        logger.info("📊 Fetching random person data...")
        person_data = await self.generate_random_person()

        # Generate AI images
        logger.info(f"🎨 Generating {num_images} AI images...")
        images = []

        for i, scenario in enumerate(self.image_scenarios[:num_images]):
            logger.info(f"Generating image {i + 1}/{num_images}: {scenario}")
            image_path = await self.generate_ai_image(person_data, scenario, i)
            if image_path:
                images.append({
                    'path': image_path,
                    'scenario': scenario,
                    'index': i + 1
                })
            else:
                logger.warning(f"Failed to generate image {i + 1}")

        # Create dossier
        dossier = {
            'person': person_data,
            'images': images,
            'generated_at': datetime.now().isoformat(),
            'total_images': len(images),
            'success_rate': len(images) / num_images * 100
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
    print("🎭 Persona Dossier Generator")
    print("=" * 50)

    async with PersonaDossierGenerator() as generator:
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

        except Exception as e:
            print(f"❌ Error: {e}")
            logger.exception("Full error details:")

if __name__ == "__main__":
    asyncio.run(main())
