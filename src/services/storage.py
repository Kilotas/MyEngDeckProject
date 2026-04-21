from contextlib import asynccontextmanager
from pathlib import Path

import aiobotocore.session

from src.core.config import settings


@asynccontextmanager
async def _s3_client():
    session = aiobotocore.session.get_session()
    async with session.create_client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        region_name="us-east-1",
    ) as client:
        yield client


class StorageService:
    """Загрузка файлов в S3-совместимое хранилище."""

    async def upload_file(self, local_path: Path, object_key: str) -> str:
        """
        Загружает файл в S3.
        Возвращает публичный URL файла.
        """
        async with _s3_client() as s3:
            with open(local_path, "rb") as f:
                await s3.put_object(
                    Bucket=settings.S3_BUCKET,
                    Key=object_key,
                    Body=f,
                    ContentType=_content_type(local_path),
                )
        return self.public_url(object_key)

    async def upload_bytes(self, data: bytes, object_key: str, content_type: str) -> str:
        """
        Загружает bytes в S3 напрямую (без временного файла).
        Возвращает публичный URL файла.
        """
        async with _s3_client() as s3:
            await s3.put_object(
                Bucket=settings.S3_BUCKET,
                Key=object_key,
                Body=data,
                ContentType=content_type,
            )
        return self.public_url(object_key)

    async def delete_file(self, object_key: str) -> None:
        async with _s3_client() as s3:
            await s3.delete_object(Bucket=settings.S3_BUCKET, Key=object_key)

    async def file_exists(self, object_key: str) -> bool:
        async with _s3_client() as s3:
            try:
                await s3.head_object(Bucket=settings.S3_BUCKET, Key=object_key)
                return True
            except Exception:
                return False

    def public_url(self, object_key: str) -> str:
        return f"{settings.S3_PUBLIC_URL}/{settings.S3_BUCKET}/{object_key}"


def _content_type(path: Path) -> str:
    types = {".mp3": "audio/mpeg", ".ogg": "audio/ogg", ".png": "image/png", ".jpg": "image/jpeg"}
    return types.get(path.suffix.lower(), "application/octet-stream")


storage = StorageService()
