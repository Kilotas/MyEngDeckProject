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
