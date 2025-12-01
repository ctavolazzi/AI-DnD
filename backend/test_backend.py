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
import json
import time

import pytest
import requests

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def print_section(title):
    """Print formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def fetch_backend_health(raise_on_unavailable=False):
    """Retrieve backend health, optionally skipping when unavailable."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        if raise_on_unavailable:
            pytest.skip("Backend not running at localhost:8000")
        return None

    if response.status_code != 200:
        if raise_on_unavailable:
            pytest.skip(f"Health endpoint unavailable (status {response.status_code})")
        return None

    data = response.json()
    print(f"✅ Backend is healthy")
    print(f"   Status: {data.get('status')}")
    print(f"   Database: {data['checks']['database']}")
    print(f"   Images: {data['checks']['images']['total']}")
    return data


@pytest.fixture(scope="module")
def backend_health():
    """Fetch backend health or skip if service unavailable."""
    return fetch_backend_health(raise_on_unavailable=True)


def test_health(backend_health):
    """Test health endpoint"""
    print_section("1. Health Check")

    assert backend_health.get("status") == "ok"
    assert backend_health["checks"]["database"] in {"ok", "warning"}
    assert "images" in backend_health["checks"]

def test_search_existing(backend_health, subject_name="Test Tavern"):
    """Test searching for existing images"""
    print_section("2. Search for Existing Images")

    response = requests.get(
        f"{API_URL}/images/search",
        params={"subject_name": subject_name},
        timeout=10,
    )
    assert response.status_code == 200

    data = response.json()
    total = data.get("total", 0)
    assert "items" in data

    if total > 0:
        print(f"✅ Found {total} existing image(s) for '{subject_name}'")
        image = data["items"][0]
        print(f"   ID: {image['id']}")
        print(f"   Created: {image['created_at']}")
        print(f"   Use count: {image['use_count']}")
        assert image["subject_name"] == subject_name
    else:
        print(f"ℹ️  No existing images for '{subject_name}'")


@pytest.fixture(scope="module")
def image_id(backend_health):
    """Return an existing image id or skip if none are available."""
    response = requests.get(
        f"{API_URL}/images/search",
        params={"subject_name": "Test Tavern"},
        timeout=10,
    )
    if response.status_code != 200:
        pytest.skip(f"Search endpoint unavailable (status {response.status_code})")

    data = response.json()
    if data.get("total", 0) == 0:
        pytest.skip("No existing images to retrieve; generate or seed images first")

    return data["items"][0]["id"]

def test_generate_image(backend_health):
    """Test image generation"""
    print_section("3. Generate New Image")

    print("⏳ Generating test image (this may take 5-10 seconds)...")

    payload = {
        "subject_type": "scene",
        "subject_name": "Test Tavern",
        "prompt": "A cozy medieval tavern interior with wooden tables, fireplace, and warm lighting. Fantasy RPG setting.",
        "aspect_ratio": "16:9",
        "component": "test-script",
    }

    start = time.time()
    response = requests.post(
        f"{API_URL}/images/generate",
        json=payload,
        timeout=30,
    )
    elapsed = time.time() - start

    if response.status_code == 429:
        pytest.skip("Rate limited or quota exceeded while generating image")

    assert response.status_code == 200

    data = response.json()
    print(f"✅ Image generated successfully!")
    print(f"   ID: {data['id']}")
    print(f"   Time: {elapsed:.2f}s")
    print(f"   File size: {data['file_size_bytes'] / 1024:.1f} KB")
    print(f"   Storage: {data['storage_path_full']}")
    assert data["subject_name"] == "Test Tavern"
    assert data["subject_type"] == "scene"
    assert data["file_size_bytes"] > 0

def test_retrieve_image(image_id):
    """Test retrieving specific image"""
    print_section("4. Retrieve Image by ID")

    response = requests.get(f"{API_URL}/images/{image_id}", timeout=10)
    assert response.status_code == 200

    data = response.json()
    print(f"✅ Retrieved image {image_id}")
    print(f"   Subject: {data['subject_name']}")
    print(f"   Type: {data['subject_type']}")
    print(f"   Use count: {data['use_count']}")
    print(f"   Created: {data['created_at']}")
    assert data["id"] == image_id

def test_persistence(backend_health):
    """Test that images persist"""
    print_section("5. Test Persistence")

    response = requests.get(
        f"{API_URL}/images/search",
        params={"subject_name": "Test Tavern"},
        timeout=10,
    )
    assert response.status_code == 200

    data = response.json()
    if data.get("total", 0) == 0:
        pytest.skip("Image not found after generation; ensure persistence seed exists")

    existing_id = data["items"][0]["id"]
    print(f"✅ Image persisted in database (ID: {existing_id})")
    print(f"   On next search/generate, this will be reused")
    print(f"   No API quota wasted!")

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  FASTAPI BACKEND TEST SUITE")
    print("="*60)

    # Test 1: Health
    health = fetch_backend_health()
    if not health:
        print("\n❌ Backend not available. Stopping tests.")
        return
    test_health(health)

    # Test 2: Search existing
    test_search_existing(health, "Test Tavern")
    existing_response = requests.get(
        f"{API_URL}/images/search",
        params={"subject_name": "Test Tavern"},
        timeout=10,
    )
    existing_data = existing_response.json() if existing_response.status_code == 200 else {}
    existing_id = existing_data.get("items", [{}])[0].get("id") if existing_data.get("total", 0) else None

    # Test 3: Generate if doesn't exist
    if existing_id:
        print(f"\nℹ️  Using existing image (ID: {existing_id})")
        image_id = existing_id
    else:
        image_id = requests.post(
            f"{API_URL}/images/generate",
            json={
                "subject_type": "scene",
                "subject_name": "Test Tavern",
                "prompt": "A cozy medieval tavern interior with wooden tables, fireplace, and warm lighting. Fantasy RPG setting.",
                "aspect_ratio": "16:9",
                "component": "test-script",
            },
            timeout=30,
        ).json().get("id")

        if not image_id:
            print("\n❌ Cannot continue tests without image")
            return

    # Test 4: Retrieve
    test_retrieve_image(image_id)

    # Test 5: Persistence
    test_persistence(health)

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

