#!/usr/bin/env python3
"""
Demo: Item Image Generation and Persistence

Shows how the backend:
1. Generates images for items
2. Stores them in database + filesystem
3. Retrieves cached images (no regeneration)
"""
import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:8000"

# Sample D&D items to generate images for
DEMO_ITEMS = [
    {
        "name": "Healing Potion",
        "description": "A glowing red potion in a glass vial with swirling magical mist"
    },
    {
        "name": "Steel Longsword",
        "description": "A well-crafted longsword with leather-wrapped hilt and polished blade"
    },
    {
        "name": "Leather Armor",
        "description": "Brown leather armor with brass buckles and shoulder guards"
    }
]


def print_header(text):
    """Print a fancy header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def check_health():
    """Check if backend is running"""
    print_header("🏥 Checking Backend Health")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        health = response.json()

        print(f"✅ Backend Status: {health['status']}")
        print(f"   Database: {health['checks']['database']}")
        print(f"   Disk Free: {health['checks']['disk_space']['free_gb']} GB")
        print(f"   Total Images: {health['checks']['images']['total']}")
        return True
    except Exception as e:
        print(f"❌ Backend not running: {e}")
        print("\nStart the backend with:")
        print("  cd backend && ./start_server.sh")
        return False


def search_for_item(item_name):
    """Search if item image already exists"""
    response = requests.get(
        f"{API_BASE}/api/v1/images/search",
        params={"subject_name": item_name, "subject_type": "item"}
    )
    data = response.json()
    return data['items']


def generate_item_image(item_name, description):
    """Generate image for an item"""
    print(f"\n📸 Generating image for: {item_name}")
    print(f"   Description: {description}")

    start = time.time()

    try:
        response = requests.post(
            f"{API_BASE}/api/v1/images/generate",
            json={
                "subject_type": "item",
                "subject_name": item_name,
                "prompt": description,
                "aspect_ratio": "1:1",
                "component": "item-modal"
            },
            timeout=30
        )

        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Generated in {elapsed:.2f}s")
            print(f"   📁 Stored at: {data['storage_path_full']}")
            print(f"   💾 Size: {data['file_size_bytes'] / 1024:.1f} KB")
            print(f"   🆔 Image ID: {data['id']}")
            return data
        elif response.status_code == 429:
            print(f"   ⚠️  Rate limit or quota exceeded")
            return None
        else:
            print(f"   ❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return None

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None


def demo_generate_phase():
    """Phase 1: Generate images for items"""
    print_header("🎨 Phase 1: Generating Item Images")

    results = []

    for item in DEMO_ITEMS:
        # Check if already exists
        existing = search_for_item(item["name"])

        if existing:
            print(f"\n💾 {item['name']} already exists (ID: {existing[0]['id']})")
            print(f"   Skipping generation (using cached)")
            results.append(existing[0])
        else:
            # Generate new
            result = generate_item_image(item["name"], item["description"])
            if result:
                results.append(result)
                time.sleep(1)  # Rate limiting courtesy

    return results


def demo_retrieval_phase():
    """Phase 2: Retrieve images (simulates app restart)"""
    print_header("🔍 Phase 2: Retrieving Cached Images (Simulated Restart)")

    print("Imagine the application just restarted...")
    print("Let's retrieve all item images from the database:\n")

    response = requests.get(
        f"{API_BASE}/api/v1/images/search",
        params={"subject_type": "item", "page": 1, "page_size": 20}
    )
    data = response.json()

    print(f"📦 Found {data['total']} item images in database:")
    print(f"   (Page {data['page']} of {data['total_pages']})\n")

    for i, item in enumerate(data['items'], 1):
        print(f"{i}. {item['subject_name']}")
        print(f"   🆔 ID: {item['id']}")
        print(f"   📁 Path: {item['storage_path_full']}")
        print(f"   👁️  Used {item['use_count']} times")
        print(f"   🕐 Created: {item['created_at'][:19]}")
        print()

    return data['items']


def demo_featured_toggle():
    """Phase 3: Mark an item as featured"""
    print_header("⭐ Phase 3: Setting Featured Images")

    # Get first item
    response = requests.get(
        f"{API_BASE}/api/v1/images/search",
        params={"subject_type": "item", "page": 1, "page_size": 1}
    )
    data = response.json()

    if not data['items']:
        print("No items found to feature")
        return

    item = data['items'][0]
    print(f"Setting '{item['subject_name']}' as featured...")

    response = requests.put(f"{API_BASE}/api/v1/images/{item['id']}/feature")
    result = response.json()

    if result['is_featured']:
        print(f"✅ '{item['subject_name']}' is now featured!")

    # Show featured items
    response = requests.get(
        f"{API_BASE}/api/v1/images/search",
        params={"is_featured": True}
    )
    featured = response.json()

    print(f"\n⭐ Featured items: {featured['total']}")
    for item in featured['items']:
        print(f"   - {item['subject_name']}")


def demo_stats():
    """Show system statistics"""
    print_header("📊 System Statistics")

    response = requests.get(f"{API_BASE}/api/v1/maintenance/stats")
    stats = response.json()

    print(f"Images:")
    print(f"  Active: {stats['images']['active']}")
    print(f"  Deleted: {stats['images']['deleted']}")
    print(f"  Storage: {stats['images']['storage_mb']} MB")

    print(f"\nCache:")
    print(f"  Total: {stats['cache']['total']}")
    print(f"  Active: {stats['cache']['active']}")
    print(f"  Expired: {stats['cache']['expired']}")


def demo_persistence_test():
    """The key demo: show images persist across 'restarts'"""
    print_header("🔄 Phase 4: Persistence Test (Key Feature)")

    print("Simulating application restart scenario:\n")

    for item in DEMO_ITEMS:
        print(f"🔍 Looking for cached image: {item['name']}")

        # Search database
        existing = search_for_item(item['name'])

        if existing:
            img = existing[0]
            print(f"   ✅ Found in database (ID: {img['id']})")
            print(f"   📁 Path exists: {img['storage_path_full']}")
            print(f"   ⚡ No API call needed - instant retrieval!")
            print(f"   💰 Saved {img['generation_time_ms']/1000:.1f}s and API quota\n")
        else:
            print(f"   ❌ Not found - would need to generate\n")


def main():
    """Run the complete demo"""
    print("\n" + "🎮" * 40)
    print("D&D ITEM IMAGE PERSISTENCE DEMO")
    print("Showing: Generate once, retrieve forever")
    print("🎮" * 40)

    # Check backend is running
    if not check_health():
        return

    # Phase 1: Generate images (or skip if cached)
    generated = demo_generate_phase()

    if not generated:
        print("\n⚠️  No images were generated (quota may be exhausted)")
        print("But we can still demonstrate retrieval of existing images...\n")

    # Phase 2: Retrieve images (simulates app restart)
    cached = demo_retrieval_phase()

    # Phase 3: Featured images
    if cached:
        demo_featured_toggle()

    # Phase 4: The key test - persistence
    demo_persistence_test()

    # Show stats
    demo_stats()

    # Final summary
    print_header("✨ Summary")
    print("Key Benefits Demonstrated:")
    print("  ✅ Images stored in database + filesystem")
    print("  ✅ Persist across application restarts")
    print("  ✅ No regeneration on subsequent runs")
    print("  ✅ Instant retrieval from cache")
    print("  ✅ Saves API quota and time")
    print("\nNext Steps:")
    print("  - View images: ls backend/images/full/")
    print("  - Database: sqlite3 backend/dnd_game.db '.schema image_assets'")
    print("  - API Docs: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()

