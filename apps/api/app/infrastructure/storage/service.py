"""Object storage base abstraction and S3/MinIO implementation."""

from __future__ import annotations

import contextlib
import io
from abc import ABC, abstractmethod
from typing import BinaryIO

import boto3
from botocore.client import Config

from app.config.settings import settings


class StorageService(ABC):
    """Abstract interface for object storage."""

    @abstractmethod
    async def upload(
        self,
        key: str,
        data: bytes | BinaryIO,
        content_type: str = "application/pdf",
    ) -> str:
        """Upload a file to storage and return its storage key."""
        pass

    @abstractmethod
    async def download(self, key: str) -> bytes:
        """Download file bytes by key."""
        pass

    @abstractmethod
    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a temporary presigned download URL."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete an object by key."""
        pass


class S3StorageService(StorageService):
    """S3-compatible object storage service (supports AWS S3 and MinIO)."""

    def __init__(self) -> None:
        self.bucket = settings.storage_bucket
        self.endpoint_url = settings.storage_endpoint
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
            region_name=settings.storage_region,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=2,
                read_timeout=5,
            ),
        )
        self._bucket_checked = False

    def _ensure_bucket_exists(self) -> None:
        if self._bucket_checked:
            return
        try:
            self.s3_client.head_bucket(Bucket=self.bucket)
            self._bucket_checked = True
        except Exception:
            with contextlib.suppress(Exception):
                self.s3_client.create_bucket(Bucket=self.bucket)
                self._bucket_checked = True

    async def upload(
        self,
        key: str,
        data: bytes | BinaryIO,
        content_type: str = "application/pdf",
    ) -> str:
        self._ensure_bucket_exists()
        fileobj = io.BytesIO(data) if isinstance(data, bytes) else data

        self.s3_client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self.bucket,
            Key=key,
            ExtraArgs={"ContentType": content_type},
        )
        return key

    async def download(self, key: str) -> bytes:
        out = io.BytesIO()
        self.s3_client.download_fileobj(Bucket=self.bucket, Key=key, Fileobj=out)
        out.seek(0)
        return out.read()

    async def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self.s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    async def delete(self, key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:
            return False
