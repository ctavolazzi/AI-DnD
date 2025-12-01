"""
PixelLab MCP Integration

Direct HTTP client for PixelLab's MCP API endpoints.
Enables generating pixel art characters, animations, and tilesets.

Based on: https://api.pixellab.ai/mcp/docs

Key features:
- Non-blocking job submission (returns job ID immediately)
- Background processing (2-5 minutes)
- Automatic status polling
- Asset caching and download management
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from enum import Enum


class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CharacterJob:
    """Tracks a character creation job."""
    character_id: str
    job_id: str
    description: str
    status: JobStatus = JobStatus.PENDING
    rotations: Dict[str, str] = field(default_factory=dict)  # direction -> image_url
    animations: Dict[str, Any] = field(default_factory=dict)
    download_url: Optional[str] = None
    error: Optional[str] = None


@dataclass
class TilesetJob:
    """Tracks a tileset creation job."""
    tileset_id: str
    job_id: str
    description: str
    status: JobStatus = JobStatus.PENDING
    tile_urls: List[str] = field(default_factory=list)
    base_tile_id: Optional[str] = None
    download_url: Optional[str] = None
    error: Optional[str] = None


class PixelLabMCPClient:
    """
    HTTP client for PixelLab MCP API.
    
    Usage:
        client = PixelLabMCPClient(api_token="your-token")
        
        # Create a character (returns immediately)
        job = client.create_character("brave knight with shining armor")
        
        # Queue animations (can be done before character completes!)
        client.animate_character(job.character_id, "walk")
        client.animate_character(job.character_id, "idle")
        
        # Check status later
        status = client.get_character_status(job.character_id)
        
        # Download when ready
        if status.status == JobStatus.COMPLETED:
            client.download_character(job.character_id, "assets/characters/")
    """
    
    BASE_URL = "https://api.pixellab.ai/mcp"
    
    # Available animation templates
    ANIMATIONS = [
        "idle", "walk", "run", "jump", "attack", "hurt", "death",
        "cast", "block", "dodge", "climb", "fall", "land"
    ]
    
    # Character proportions presets
    PROPORTIONS = [
        "default", "chibi", "cartoon", "stylized",
        "realistic_male", "realistic_female", "heroic"
    ]
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the PixelLab MCP client.
        
        Args:
            api_token: PixelLab API token. Falls back to PIXELLAB_API_KEY env var.
        """
        self.api_token = api_token or os.getenv("PIXELLAB_API_KEY")
        if not self.api_token:
            raise ValueError(
                "PixelLab API token required. Set PIXELLAB_API_KEY env var or pass api_token."
            )
        
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Job tracking
        self.character_jobs: Dict[str, CharacterJob] = {}
        self.tileset_jobs: Dict[str, TilesetJob] = {}
        
        # Asset cache directory
        self.cache_dir = Path("game_assets")
        self.cache_dir.mkdir(exist_ok=True)
    
    def _call_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make an MCP tool call."""
        # MCP uses a specific endpoint format
        url = f"{self.BASE_URL}/tools/{tool_name}"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=params,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e), "status": "failed"}
    
    # =========================================================================
    # CHARACTER CREATION
    # =========================================================================
    
    def create_character(
        self,
        description: str,
        name: Optional[str] = None,
        n_directions: int = 8,
        size: int = 48,
        proportions: str = "default",
        outline: str = "single color black outline",
        shading: str = "basic shading",
        detail: str = "medium detail",
        view: str = "low top-down"
    ) -> CharacterJob:
        """
        Queue a character creation job.
        
        Args:
            description: Character description (e.g., "brave knight with shining armor")
            name: Optional character name
            n_directions: 4 or 8 directional views
            size: Canvas size in pixels (16-128, character ~60% of height)
            proportions: Body proportions preset
            outline: Outline style
            shading: Shading style
            detail: Detail level
            view: Camera view angle
        
        Returns:
            CharacterJob with character_id for tracking
        """
        params = {
            "description": description,
            "n_directions": n_directions,
            "size": size,
            "proportions": json.dumps({"type": "preset", "name": proportions}),
            "outline": outline,
            "shading": shading,
            "detail": detail,
            "view": view
        }
        
        if name:
            params["name"] = name
        
        result = self._call_tool("create_character", params)
        
        if "error" in result:
            job = CharacterJob(
                character_id="",
                job_id="",
                description=description,
                status=JobStatus.FAILED,
                error=result["error"]
            )
        else:
            job = CharacterJob(
                character_id=result.get("character_id", ""),
                job_id=result.get("job_id", ""),
                description=description,
                status=JobStatus.PROCESSING
            )
            self.character_jobs[job.character_id] = job
        
        return job
    
    def animate_character(
        self,
        character_id: str,
        animation: str,
        action_description: Optional[str] = None,
        animation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Queue an animation job for an existing character.
        
        Can be called immediately after create_character (no waiting needed!)
        
        Args:
            character_id: From create_character result
            animation: Template animation ID (walk, idle, attack, etc.)
            action_description: Optional custom action description
            animation_name: Optional custom name for the animation
        
        Returns:
            Job info dict
        """
        params = {
            "character_id": character_id,
            "template_animation_id": animation
        }
        
        if action_description:
            params["action_description"] = action_description
        if animation_name:
            params["animation_name"] = animation_name
        
        return self._call_tool("animate_character", params)
    
    def get_character_status(self, character_id: str) -> CharacterJob:
        """
        Get complete character info including rotations and animations.
        
        Args:
            character_id: Character ID to check
        
        Returns:
            Updated CharacterJob with current status
        """
        result = self._call_tool("get_character", {
            "character_id": character_id,
            "include_preview": True
        })
        
        job = self.character_jobs.get(character_id) or CharacterJob(
            character_id=character_id,
            job_id="",
            description=""
        )
        
        if "error" in result:
            job.status = JobStatus.FAILED
            job.error = result["error"]
        else:
            status_str = result.get("status", "processing").lower()
            job.status = JobStatus(status_str) if status_str in [s.value for s in JobStatus] else JobStatus.PROCESSING
            job.rotations = result.get("rotations", {})
            job.animations = result.get("animations", {})
            job.download_url = result.get("download_url")
        
        self.character_jobs[character_id] = job
        return job
    
    def list_characters(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List all created characters."""
        return self._call_tool("list_characters", {"limit": limit, "offset": offset})
    
    def delete_character(self, character_id: str) -> Dict[str, Any]:
        """Delete a character and all its data."""
        result = self._call_tool("delete_character", {"character_id": character_id})
        if character_id in self.character_jobs:
            del self.character_jobs[character_id]
        return result
    
    # =========================================================================
    # TILESET CREATION
    # =========================================================================
    
    def create_topdown_tileset(
        self,
        lower_description: str,
        upper_description: str,
        tile_size: int = 16,
        transition_size: float = 0.25,
        lower_base_tile_id: Optional[str] = None
    ) -> TilesetJob:
        """
        Create a Wang tileset for top-down games.
        
        Creates 16 tiles covering all corner combinations for seamless terrain.
        
        Args:
            lower_description: Base terrain (e.g., "ocean water")
            upper_description: Transition terrain (e.g., "sandy beach")
            tile_size: Tile dimensions (typically 16 or 32)
            transition_size: Blend width (0=sharp, 0.5=wide)
            lower_base_tile_id: Chain from previous tileset for consistency
        
        Returns:
            TilesetJob for tracking
        """
        params = {
            "lower_description": lower_description,
            "upper_description": upper_description,
            "tile_size": {"width": tile_size, "height": tile_size},
            "transition_size": transition_size
        }
        
        if lower_base_tile_id:
            params["lower_base_tile_id"] = lower_base_tile_id
        
        result = self._call_tool("create_topdown_tileset", params)
        
        description = f"{lower_description} → {upper_description}"
        
        if "error" in result:
            job = TilesetJob(
                tileset_id="",
                job_id="",
                description=description,
                status=JobStatus.FAILED,
                error=result["error"]
            )
        else:
            job = TilesetJob(
                tileset_id=result.get("tileset_id", ""),
                job_id=result.get("job_id", ""),
                description=description,
                status=JobStatus.PROCESSING,
                base_tile_id=result.get("upper_base_tile_id")
            )
            self.tileset_jobs[job.tileset_id] = job
        
        return job
    
    def create_sidescroller_tileset(
        self,
        lower_description: str,
        transition_description: str,
        tile_size: int = 16,
        transition_size: float = 0.25,
        base_tile_id: Optional[str] = None
    ) -> TilesetJob:
        """
        Create a tileset for 2D platformer games.
        
        Args:
            lower_description: Platform material (stone, wood, etc.)
            transition_description: Top decoration (grass, moss, etc.)
            tile_size: Tile dimensions
            transition_size: Decoration coverage (0=none, 0.5=heavy)
            base_tile_id: Chain from previous tileset
        
        Returns:
            TilesetJob for tracking
        """
        params = {
            "lower_description": lower_description,
            "transition_description": transition_description,
            "tile_size": {"width": tile_size, "height": tile_size},
            "transition_size": transition_size
        }
        
        if base_tile_id:
            params["base_tile_id"] = base_tile_id
        
        result = self._call_tool("create_sidescroller_tileset", params)
        
        description = f"{lower_description} + {transition_description}"
        
        if "error" in result:
            job = TilesetJob(
                tileset_id="",
                job_id="",
                description=description,
                status=JobStatus.FAILED,
                error=result["error"]
            )
        else:
            job = TilesetJob(
                tileset_id=result.get("tileset_id", ""),
                job_id=result.get("job_id", ""),
                description=description,
                status=JobStatus.PROCESSING,
                base_tile_id=result.get("base_tile_id")
            )
            self.tileset_jobs[job.tileset_id] = job
        
        return job
    
    def get_tileset_status(self, tileset_id: str, tileset_type: str = "topdown") -> TilesetJob:
        """Get tileset status and download info."""
        tool = f"get_{tileset_type}_tileset" if tileset_type != "topdown" else "get_topdown_tileset"
        result = self._call_tool(tool, {
            "tileset_id": tileset_id,
            "include_example_map": True
        })
        
        job = self.tileset_jobs.get(tileset_id) or TilesetJob(
            tileset_id=tileset_id,
            job_id="",
            description=""
        )
        
        if "error" in result:
            job.status = JobStatus.FAILED
            job.error = result["error"]
        else:
            status_str = result.get("status", "processing").lower()
            job.status = JobStatus(status_str) if status_str in [s.value for s in JobStatus] else JobStatus.PROCESSING
            job.tile_urls = result.get("tile_urls", [])
            job.download_url = result.get("download_url")
        
        self.tileset_jobs[tileset_id] = job
        return job
    
    # =========================================================================
    # ISOMETRIC TILES
    # =========================================================================
    
    def create_isometric_tile(
        self,
        description: str,
        size: int = 32,
        tile_shape: str = "block",
        outline: str = "lineless",
        shading: str = "basic shading",
        detail: str = "medium detail"
    ) -> Dict[str, Any]:
        """
        Create an isometric tile.
        
        Args:
            description: Tile description
            size: Tile size (32px recommended)
            tile_shape: thin (floors), thick (platforms), block (cubes)
            outline: lineless or single color
            shading: Shading style
            detail: Detail level
        
        Returns:
            Tile info with tile_id
        """
        return self._call_tool("create_isometric_tile", {
            "description": description,
            "size": size,
            "tile_shape": tile_shape,
            "outline": outline,
            "shading": shading,
            "detail": detail
        })
    
    def get_isometric_tile(self, tile_id: str) -> Dict[str, Any]:
        """Get isometric tile status and data."""
        return self._call_tool("get_isometric_tile", {"tile_id": tile_id})
    
    # =========================================================================
    # MAP OBJECTS
    # =========================================================================
    
    def create_map_object(
        self,
        description: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        view: str = "high top-down",
        outline: str = "single color outline",
        shading: str = "medium shading",
        detail: str = "medium detail"
    ) -> Dict[str, Any]:
        """
        Create a map object with transparent background.
        
        Args:
            description: Object description
            width: Object width (optional)
            height: Object height (optional)
            view: Camera view
            outline: Outline style
            shading: Shading style
            detail: Detail level
        
        Returns:
            Object info with object_id
        """
        params = {
            "description": description,
            "view": view,
            "outline": outline,
            "shading": shading,
            "detail": detail
        }
        
        if width:
            params["width"] = width
        if height:
            params["height"] = height
        
        return self._call_tool("create_map_object", params)
    
    def get_map_object(self, object_id: str) -> Dict[str, Any]:
        """Get map object status."""
        return self._call_tool("get_map_object", {"object_id": object_id})
    
    # =========================================================================
    # ASSET MANAGEMENT
    # =========================================================================
    
    def download_asset(self, url: str, save_path: str) -> bool:
        """
        Download an asset from PixelLab.
        
        Args:
            url: Download URL from job status
            save_path: Local path to save the asset
        
        Returns:
            True if successful
        """
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            path = Path(save_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(response.content)
            
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            return False
    
    def wait_for_character(
        self,
        character_id: str,
        timeout: int = 300,
        poll_interval: int = 10
    ) -> CharacterJob:
        """
        Wait for a character to complete processing.
        
        Args:
            character_id: Character ID to wait for
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
        
        Returns:
            Final CharacterJob status
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = self.get_character_status(character_id)
            
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return job
            
            print(f"Character {character_id}: {job.status.value}...")
            time.sleep(poll_interval)
        
        job = self.character_jobs.get(character_id, CharacterJob(
            character_id=character_id, job_id="", description=""
        ))
        job.status = JobStatus.FAILED
        job.error = "Timeout waiting for character generation"
        return job
    
    def wait_for_tileset(
        self,
        tileset_id: str,
        tileset_type: str = "topdown",
        timeout: int = 300,
        poll_interval: int = 10
    ) -> TilesetJob:
        """
        Wait for a tileset to complete processing.
        
        Args:
            tileset_id: Tileset ID to wait for
            tileset_type: "topdown" or "sidescroller"
            timeout: Maximum wait time in seconds
            poll_interval: Time between status checks
        
        Returns:
            Final TilesetJob status
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            job = self.get_tileset_status(tileset_id, tileset_type)
            
            if job.status in (JobStatus.COMPLETED, JobStatus.FAILED):
                return job
            
            print(f"Tileset {tileset_id}: {job.status.value}...")
            time.sleep(poll_interval)
        
        job = self.tileset_jobs.get(tileset_id, TilesetJob(
            tileset_id=tileset_id, job_id="", description=""
        ))
        job.status = JobStatus.FAILED
        job.error = "Timeout waiting for tileset generation"
        return job


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_game_assets(api_token: str, output_dir: str = "game_assets") -> Dict[str, Any]:
    """
    Generate a complete set of game assets.
    
    Creates:
    - Hero character with walk, idle, attack animations
    - Goblin enemy with walk, idle animations
    - Skeleton enemy with walk, attack animations
    - Dungeon tileset (stone floor → dark stone wall)
    - Forest tileset (grass → dirt path)
    
    Args:
        api_token: PixelLab API token
        output_dir: Directory to save assets
    
    Returns:
        Dict with all job IDs and statuses
    """
    client = PixelLabMCPClient(api_token)
    
    jobs = {
        "characters": [],
        "tilesets": []
    }
    
    # Create hero character
    print("Creating hero character...")
    hero = client.create_character(
        description="brave knight with shining silver armor and blue cape",
        name="Hero",
        n_directions=8,
        size=48,
        proportions="heroic"
    )
    jobs["characters"].append({"name": "hero", "job": hero})
    
    # Queue hero animations immediately
    client.animate_character(hero.character_id, "walk", "walking confidently")
    client.animate_character(hero.character_id, "idle", "standing ready")
    client.animate_character(hero.character_id, "attack", "sword slash")
    
    # Create goblin enemy
    print("Creating goblin enemy...")
    goblin = client.create_character(
        description="small green goblin with ragged clothes and crude dagger",
        name="Goblin",
        n_directions=4,
        size=32,
        proportions="chibi"
    )
    jobs["characters"].append({"name": "goblin", "job": goblin})
    
    client.animate_character(goblin.character_id, "walk")
    client.animate_character(goblin.character_id, "idle")
    
    # Create skeleton enemy
    print("Creating skeleton enemy...")
    skeleton = client.create_character(
        description="animated skeleton warrior with rusty sword and shield",
        name="Skeleton",
        n_directions=4,
        size=48
    )
    jobs["characters"].append({"name": "skeleton", "job": skeleton})
    
    client.animate_character(skeleton.character_id, "walk")
    client.animate_character(skeleton.character_id, "attack")
    
    # Create dungeon tileset
    print("Creating dungeon tileset...")
    dungeon = client.create_topdown_tileset(
        lower_description="dark stone dungeon floor",
        upper_description="stone brick wall",
        tile_size=32
    )
    jobs["tilesets"].append({"name": "dungeon", "job": dungeon})
    
    # Create forest tileset
    print("Creating forest tileset...")
    forest = client.create_topdown_tileset(
        lower_description="green grass meadow",
        upper_description="dirt path",
        tile_size=32
    )
    jobs["tilesets"].append({"name": "forest", "job": forest})
    
    print(f"\nAll jobs submitted! Assets will be ready in 2-5 minutes.")
    print(f"Character IDs: {[j['job'].character_id for j in jobs['characters']]}")
    print(f"Tileset IDs: {[j['job'].tileset_id for j in jobs['tilesets']]}")
    
    return jobs


if __name__ == "__main__":
    # Demo usage
    import sys
    
    token = os.getenv("PIXELLAB_API_KEY")
    if not token:
        print("Set PIXELLAB_API_KEY environment variable")
        sys.exit(1)
    
    jobs = generate_game_assets(token)
    print(f"\nSubmitted {len(jobs['characters'])} characters and {len(jobs['tilesets'])} tilesets")

