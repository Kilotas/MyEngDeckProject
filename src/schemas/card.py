import uuid
from datetime import datetime

from pydantic import BaseModel


class CardCreate(BaseModel):
    word: str
    translation: str
    example: str | None = None
    audio_path: str | None = None
    image_path: str | None = None


class CardUpdate(BaseModel):
    word: str | None = None
    translation: str | None = None
    example: str | None = None
    audio_path: str | None = None
    image_path: str | None = None


class CardRead(BaseModel):
    id: uuid.UUID
    word: str
    translation: str
    example: str | None
    audio_path: str | None
    image_path: str | None
    deck_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
