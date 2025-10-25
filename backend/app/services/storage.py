"""Filesystem storage service with WebP compression"""
from pathlib import Path
from PIL import Image
from io import BytesIO
import hashlib
from datetime import datetime
from typing import Dict


class StorageService:
    """Handles filesystem storage with WebP compression and thumbnail generation"""

    def __init__(self, base_dir: str = "images"):
        """
        Initialize storage service

        Args:
            base_dir: Base directory for image storage
        """
        self.base_dir = Path(base_dir)
        self.full_dir = self.base_dir / "full"
        self.thumb_dir = self.base_dir / "thumbnails"

        # Create directories if they don't exist
        self.full_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir.mkdir(parents=True, exist_ok=True)

    def save_image(self, image_data: bytes, subject_name: str) -> Dict[str, any]:
        """
        Save image with WebP compression and thumbnail

        Args:
            image_data: Raw image bytes (PNG format from Gemini)
            subject_name: Subject name for filename

        Returns:
            Dictionary with full_path, thumbnail_path, and file_size_bytes
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(image_data).hexdigest()[:8]
        # Sanitize subject name for filename
        safe_subject = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in subject_name)
        safe_subject = safe_subject.replace(' ', '_')[:50]  # Limit length
        filename = f"{safe_subject}_{timestamp}_{content_hash}.webp"

        # Load image from bytes
        img = Image.open(BytesIO(image_data))

        # Save full size (WebP, 85% quality)
        full_path = self.full_dir / filename
        img.save(full_path, "WEBP", quality=85)
        full_size = full_path.stat().st_size

        # Save thumbnail (200x200)
        img_thumb = img.copy()
        img_thumb.thumbnail((200, 200), Image.Resampling.LANCZOS)
        thumb_path = self.thumb_dir / filename
        img_thumb.save(thumb_path, "WEBP", quality=80)

        return {
            "full_path": str(full_path),
            "thumbnail_path": str(thumb_path),
            "file_size_bytes": full_size
        }

    def get_image(self, path: str) -> bytes:
        """
        Read image from filesystem

        Args:
            path: File path to read

        Returns:
            Image bytes
        """
        return Path(path).read_bytes()

    def delete_image(self, full_path: str, thumb_path: str) -> None:
        """
        Delete both full and thumbnail images

        Args:
            full_path: Path to full size image
            thumb_path: Path to thumbnail
        """
        Path(full_path).unlink(missing_ok=True)
        Path(thumb_path).unlink(missing_ok=True)

