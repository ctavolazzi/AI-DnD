#!/usr/bin/env python3
"""
Asset Status Checker

Check the status of pending PixelLab asset generation jobs.

Usage:
    python scripts/check_assets.py
    python scripts/check_assets.py --download  # Download completed assets
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pygame_mvp.services.pixellab_mcp import PixelLabMCPClient, JobStatus


def main():
    parser = argparse.ArgumentParser(description="Check asset generation status")
    parser.add_argument("--download", action="store_true", help="Download completed assets")
    parser.add_argument("--character", help="Check specific character ID")
    parser.add_argument("--tileset", help="Check specific tileset ID")
    args = parser.parse_args()
    
    # Get API key
    api_key = os.getenv("PIXELLAB_API_KEY")
    if not api_key:
        # Try loading from .env
        env_file = project_root / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("PIXELLAB_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    
    if not api_key:
        print("❌ Error: PIXELLAB_API_KEY not found")
        sys.exit(1)
    
    try:
        client = PixelLabMCPClient(api_key)
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    print("🔍 Asset Status Checker")
    print("=" * 50)
    
    # Load pending jobs
    job_file = project_root / "game_assets" / "pending_jobs.json"
    if not job_file.exists() and not args.character and not args.tileset:
        print("No pending jobs found. Run scripts/generate_assets.py first.")
        sys.exit(0)
    
    jobs = {"characters": [], "tilesets": []}
    if job_file.exists():
        jobs = json.loads(job_file.read_text())
    
    # Check specific asset if provided
    if args.character:
        jobs["characters"] = [{"name": "requested", "id": args.character}]
    if args.tileset:
        jobs["tilesets"] = [{"name": "requested", "id": args.tileset}]
    
    # Check characters
    if jobs.get("characters"):
        print("\n🦸 Characters:")
        print("-" * 30)
        
        completed = []
        for char in jobs["characters"]:
            status = client.get_character_status(char["id"])
            status_icon = {
                JobStatus.COMPLETED: "✅",
                JobStatus.PROCESSING: "⏳",
                JobStatus.PENDING: "🔄",
                JobStatus.FAILED: "❌"
            }.get(status.status, "❓")
            
            print(f"  {status_icon} {char['name']}: {status.status.value}")
            
            if status.status == JobStatus.COMPLETED:
                completed.append(char)
                if status.download_url:
                    print(f"      Download: {status.download_url}")
                if status.rotations:
                    print(f"      Rotations: {len(status.rotations)} directions")
                if status.animations:
                    print(f"      Animations: {list(status.animations.keys())}")
            elif status.error:
                print(f"      Error: {status.error}")
        
        # Download completed assets
        if args.download and completed:
            print("\n📥 Downloading completed characters...")
            output_dir = project_root / "game_assets" / "characters"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for char in completed:
                status = client.get_character_status(char["id"])
                if status.download_url:
                    save_path = output_dir / f"{char['name']}.zip"
                    if client.download_asset(status.download_url, str(save_path)):
                        print(f"  ✅ Saved: {save_path}")
                    else:
                        print(f"  ❌ Failed to download {char['name']}")
    
    # Check tilesets
    if jobs.get("tilesets"):
        print("\n🏰 Tilesets:")
        print("-" * 30)
        
        completed = []
        for ts in jobs["tilesets"]:
            status = client.get_tileset_status(ts["id"])
            status_icon = {
                JobStatus.COMPLETED: "✅",
                JobStatus.PROCESSING: "⏳",
                JobStatus.PENDING: "🔄",
                JobStatus.FAILED: "❌"
            }.get(status.status, "❓")
            
            print(f"  {status_icon} {ts['name']}: {status.status.value}")
            
            if status.status == JobStatus.COMPLETED:
                completed.append(ts)
                if status.download_url:
                    print(f"      Download: {status.download_url}")
                if status.tile_urls:
                    print(f"      Tiles: {len(status.tile_urls)}")
            elif status.error:
                print(f"      Error: {status.error}")
        
        # Download completed tilesets
        if args.download and completed:
            print("\n📥 Downloading completed tilesets...")
            output_dir = project_root / "game_assets" / "tilesets"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            for ts in completed:
                status = client.get_tileset_status(ts["id"])
                if status.download_url:
                    save_path = output_dir / f"{ts['name']}.zip"
                    if client.download_asset(status.download_url, str(save_path)):
                        print(f"  ✅ Saved: {save_path}")
                    else:
                        print(f"  ❌ Failed to download {ts['name']}")
    
    print("\n" + "=" * 50)
    print("Run with --download to save completed assets")


if __name__ == "__main__":
    main()

