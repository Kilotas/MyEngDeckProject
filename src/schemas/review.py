import uuid
from datetime import datetime

from pydantic import BaseModel


class ReviewRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    card_id: uuid.UUID
    easiness_factor: float
    interval: int
    repetitions: int
    last_reviewed_at: datetime | None
    next_review_at: datetime

    model_config = {"from_attributes": True}


class DeckStats(BaseModel):
    total_cards: int
    new_cards: int
    reviewed_cards: int
    due_cards: int
    learned_cards: int
    avg_interval: float
    learn_available: int
