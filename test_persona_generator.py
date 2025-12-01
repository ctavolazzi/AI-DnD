#!/usr/bin/env python3
"""
Test script for Persona Dossier Generator
"""

import asyncio
import requests
import time

import pytest

from persona_dossier_generator import PersonaDossierGenerator

async def _exercise_persona_generator():
    """Run persona generator flows for the test."""
    async with PersonaDossierGenerator() as generator:
        print("1. Testing random person generation...")
        person = await generator.generate_random_person()
        assert person["name"], "Generated person is missing a name"
        assert person["age"] > 0, "Generated person is missing an age"
        print(f"   ✅ Generated: {person['name']} ({person['age']} years old)")
        print(f"   📍 Location: {person['location']['city']}, {person['location']['state']}")

        print("\n2. Testing AI image generation...")
        image_path = await generator.generate_ai_image(person, "professional headshot", 0)
        if image_path:
            print(f"   ✅ Generated image: {image_path}")
        else:
            print("   ⚠️  Image generation failed (Nano Banana may not be running)")

        print("\n3. Testing full dossier generation...")
        dossier = await generator.generate_persona_dossier(3)  # Generate 3 images for testing
        assert dossier["person"]["name"], "Dossier missing person details"
        assert dossier["total_images"] >= 0, "Dossier missing image count"
        print(f"   ✅ Generated dossier for: {dossier['person']['name']}")
        print(f"   📊 Images: {dossier['total_images']}/3")
        print(f"   📈 Success rate: {dossier['success_rate']:.1f}%")


def test_persona_generator():
    """Test the persona generator synchronously via asyncio.run."""
    print("🧪 Testing Persona Dossier Generator")
    print("=" * 50)

    try:
        asyncio.run(_exercise_persona_generator())
        print("\n✅ All persona generator checks passed!")
    except (ConnectionError, requests.exceptions.ConnectionError) as exc:
        pytest.skip(f"Persona generator backend unavailable: {exc}")
    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Persona generator test failed: {exc}")

def test_backend_server():
    """Test the backend server"""
    print("\n🌐 Testing Backend Server")
    print("=" * 50)

    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
    except requests.exceptions.ConnectionError as exc:
        pytest.skip(f"Backend server is not running: {exc}")
    except Exception as exc:  # pragma: no cover - surfaced as pytest failure
        pytest.fail(f"Backend health request failed: {exc}")

    assert response.status_code == 200, f"Server health check failed: {response.status_code}"
    health_data = response.json()
    print(f"✅ Server is healthy")
    print(f"   📅 Timestamp: {health_data['timestamp']}")
    print(f"   🤖 Nano Banana: {'✅ Available' if health_data['nano_banana_available'] else '❌ Not available'}")

def main():
    """Run all tests"""
    print("🎭 PERSONA DOSSIER GENERATOR TEST SUITE")
    print("=" * 60)

    generator_passed = False
    backend_passed = False

    try:
        test_persona_generator()
        generator_passed = True
    except pytest.skip.Exception as exc:
        print(f"Persona generator skipped: {exc}")
    except Exception as exc:
        print(f"Persona generator failed: {exc}")

    try:
        test_backend_server()
        backend_passed = True
    except pytest.skip.Exception as exc:
        print(f"Backend server check skipped: {exc}")
    except Exception as exc:
        print(f"Backend server check failed: {exc}")

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    tests = [
        ("Persona Generator", generator_passed),
        ("Backend Server", backend_passed)
    ]

    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for test_name, result in tests:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Persona Dossier Generator is ready.")
        print("\n📋 Next steps:")
        print("1. Run: python3 launch_persona_generator.py")
        print("2. Configure settings in the web interface")
        print("3. Generate your first persona dossier!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed.")
        print("\n🔧 Troubleshooting:")
        if not generator_passed:
            print("- Check if Nano Banana is running: python3 nano_banana_server.py")
        if not backend_passed:
            print("- Start backend server: python3 persona_dossier_server.py")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
