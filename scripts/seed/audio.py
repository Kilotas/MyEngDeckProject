"""Генерация аудио через edge-tts и загрузка в MinIO."""

import asyncio

import edge_tts

from src.services.storage import StorageService

VOICE = "en-US-JennyNeural"  # Microsoft Neural TTS (бесплатно, без ключей)

storage = StorageService()


async def _generate_bytes(word: str) -> bytes:
    """Генерирует MP3-байты для слова через Microsoft TTS."""
    communicate = edge_tts.Communicate(word, VOICE)
    chunks = []
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            chunks.append(chunk["data"])
    return b"".join(chunks)


async def upload_audio(sem: asyncio.Semaphore, word: str) -> str | None:
    """
    Генерирует аудио и загружает в MinIO.
    Если файл уже есть в MinIO — пропускает генерацию.
    Возвращает object_key (путь в MinIO) или None при ошибке.
    """
    object_key = f"audio/{word}.mp3"
    async with sem:
        try:
            if await storage.file_exists(object_key):
                return object_key
            audio_bytes = await _generate_bytes(word)
            if audio_bytes:
                await storage.upload_bytes(audio_bytes, object_key, "audio/mpeg")
                return object_key
        except Exception as e:
            print(f"  [WARN] Аудио не удалось для '{word}': {e}")
    return None
