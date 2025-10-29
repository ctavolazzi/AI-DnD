"""PixelLab API integration service."""
import httpx
from app.config import settings


async def generate_sprite(prompt: str, size: int = 64, no_background: bool = True) -> bytes:
    """
    Generate pixel art sprite using PixelLab API.

    Args:
        prompt: Description of sprite to generate
        size: Size in pixels (width and height)
        no_background: Whether to generate without background

    Returns:
        bytes: PNG image data
    """
    if not settings.pixellab_api_key:
        raise ValueError("PixelLab API key not configured")

    url = "https://api.pixellab.ai/generate"  # Update with actual PixelLab API endpoint

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            json={
                "prompt": prompt,
                "width": size,
                "height": size,
                "no_background": no_background
            },
            headers={
                "Authorization": f"Bearer {settings.pixellab_api_key}",
                "Content-Type": "application/json"
            }
        )
        response.raise_for_status()
        return response.content

