"""Storage service for image uploads (local or S3)."""
import os
import base64
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError

from app.config import settings


class StorageService:
    """Handle image storage (local filesystem or S3)."""

    def __init__(self):
        self.backend = settings.storage_backend
        if self.backend == "s3":
            self.s3_client = boto3.client(
                's3',
                region_name=settings.s3_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
        else:
            # Ensure upload directory exists
            Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

    async def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        Upload image and return URL/path.

        Args:
            image_data: Image bytes
            filename: Desired filename (e.g., "sprites/user_123/knight.png")

        Returns:
            str: URL or path to uploaded image
        """
        if self.backend == "s3":
            return await self._upload_to_s3(image_data, filename)
        else:
            return await self._upload_to_local(image_data, filename)

    async def _upload_to_local(self, image_data: bytes, filename: str) -> str:
        """Upload to local filesystem."""
        filepath = Path(settings.upload_dir) / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(image_data)

        # Return relative path
        return f"/uploads/{filename}"

    async def _upload_to_s3(self, image_data: bytes, filename: str) -> str:
        """Upload to S3."""
        try:
            self.s3_client.put_object(
                Bucket=settings.s3_bucket,
                Key=filename,
                Body=image_data,
                ContentType='image/png'
            )
            # Return S3 URL
            return f"https://{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/{filename}"
        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")

    async def get_image(self, url_or_path: str) -> bytes:
        """
        Download image from storage.

        Args:
            url_or_path: URL or local path to image

        Returns:
            bytes: Image data
        """
        if url_or_path.startswith('http'):
            return await self._download_from_s3(url_or_path)
        else:
            return await self._read_from_local(url_or_path)

    async def _read_from_local(self, path: str) -> bytes:
        """Read from local filesystem."""
        # Remove /uploads/ prefix if present
        clean_path = path.lstrip('/uploads/')
        filepath = Path(settings.upload_dir) / clean_path

        with open(filepath, 'rb') as f:
            return f.read()

    async def _download_from_s3(self, url: str) -> bytes:
        """Download from S3."""
        # Extract key from URL
        key = url.split(f"{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/")[1]

        try:
            response = self.s3_client.get_object(
                Bucket=settings.s3_bucket,
                Key=key
            )
            return response['Body'].read()
        except ClientError as e:
            raise Exception(f"S3 download failed: {str(e)}")


# Global storage instance
storage = StorageService()

