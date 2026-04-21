import uuid
from datetime import datetime

from pydantic import BaseModel

from src.db.models.deck import DifficultyLevel


class DeckCreate(BaseModel):
    name: str
    description: str | None = None
    level: DifficultyLevel


class DeckUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    level: DifficultyLevel | None = None


class DeckRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    level: DifficultyLevel
    is_system: bool
    owner_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}
