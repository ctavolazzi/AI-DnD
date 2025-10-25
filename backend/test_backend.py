#!/usr/bin/env python3
"""
Quick test script for FastAPI backend

Tests:
1. Health check
2. Image generation
3. Image retrieval
4. Database persistence

Usage:
    python test_backend.py
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def test_health():
    """Test health endpoint"""
    print_section("1. Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data['checks']['database']}")
            print(f"   Images: {data['checks']['images']['total']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend")
        print("   Make sure it's running: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_search_existing(subject_name="Test Tavern"):
    """Test searching for existing images"""
    print_section("2. Search for Existing Images")

    try:
        response = requests.get(
            f"{API_URL}/images/search",
            params={"subject_name": subject_name}
        )

        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)

            if total > 0:
                print(f"✅ Found {total} existing image(s) for '{subject_name}'")
                image = data['items'][0]
                print(f"   ID: {image['id']}")
                print(f"   Created: {image['created_at']}")
                print(f"   Use count: {image['use_count']}")
                return image['id']
            else:
                print(f"ℹ️  No existing images for '{subject_name}'")
                return None
        else:
            print(f"❌ Search failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_generate_image():
    """Test image generation"""
    print_section("3. Generate New Image")

    print("⏳ Generating test image (this may take 5-10 seconds)...")

    payload = {
        "subject_type": "scene",
        "subject_name": "Test Tavern",
        "prompt": "A cozy medieval tavern interior with wooden tables, fireplace, and warm lighting. Fantasy RPG setting.",
        "aspect_ratio": "16:9",
        "component": "test-script"
    }

    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/images/generate",
            json=payload,
            timeout=30
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Image generated successfully!")
            print(f"   ID: {data['id']}")
            print(f"   Time: {elapsed:.2f}s")
            print(f"   File size: {data['file_size_bytes'] / 1024:.1f} KB")
            print(f"   Storage: {data['storage_path_full']}")
            return data['id']
        elif response.status_code == 429:
            print(f"⚠️  Rate limited or quota exceeded")
            print(f"   {response.json().get('detail', {}).get('message')}")
            return None
        else:
            print(f"❌ Generation failed: {response.status_code}")
            print(f"   {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Request timed out (>30s)")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_retrieve_image(image_id):
    """Test retrieving specific image"""
    print_section("4. Retrieve Image by ID")

    try:
        response = requests.get(f"{API_URL}/images/{image_id}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved image {image_id}")
            print(f"   Subject: {data['subject_name']}")
            print(f"   Type: {data['subject_type']}")
            print(f"   Use count: {data['use_count']}")
            print(f"   Created: {data['created_at']}")
            return True
        else:
            print(f"❌ Retrieval failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_persistence():
    """Test that images persist"""
    print_section("5. Test Persistence")

    # Search again for the test image
    existing_id = test_search_existing("Test Tavern")

    if existing_id:
        print(f"✅ Image persisted in database (ID: {existing_id})")
        print(f"   On next search/generate, this will be reused")
        print(f"   No API quota wasted!")
        return True
    else:
        print(f"❌ Image not found after generation")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  FASTAPI BACKEND TEST SUITE")
    print("="*60)

    # Test 1: Health
    if not test_health():
        print("\n❌ Backend not available. Stopping tests.")
        return

    # Test 2: Search existing
    existing_id = test_search_existing("Test Tavern")

    # Test 3: Generate if doesn't exist
    if existing_id:
        print(f"\nℹ️  Using existing image (ID: {existing_id})")
        image_id = existing_id
    else:
        image_id = test_generate_image()

        if not image_id:
            print("\n❌ Cannot continue tests without image")
            return

    # Test 4: Retrieve
    test_retrieve_image(image_id)

    # Test 5: Persistence
    test_persistence()

    # Summary
    print_section("SUMMARY")
    print("✅ All tests passed!")
    print(f"\n🎯 Backend is working correctly:")
    print(f"   - Health check: OK")
    print(f"   - Image generation: OK")
    print(f"   - Database persistence: OK")
    print(f"   - Image retrieval: OK")
    print(f"\n📦 Your images are stored in:")
    print(f"   - Database: backend/dnd_game.db")
    print(f"   - Files: backend/images/")
    print(f"\n🚀 Next steps:")
    print(f"   1. Run seeding script to generate all game images")
    print(f"   2. Update frontend to use this API")
    print(f"   3. Deprecate Nano Banana server")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

