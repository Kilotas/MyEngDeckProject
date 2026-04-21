import uuid
from datetime import datetime, timezone, timedelta

from src.core.exceptions import NotFoundError
from src.db.models.review import Review
from src.schemas.review import ReviewRead
from src.uow.base import AbstractUoW


def _apply_sm2(review: Review, quality: int) -> None:
    """Обновляет SM-2 поля на основе оценки качества (0–5)."""
    if quality < 3:
        review.repetitions = 0
        review.interval = 1
    else:
        if review.repetitions == 0:
            review.interval = 1
        elif review.repetitions == 1:
            review.interval = 6
        else:
            review.interval = round(review.interval * review.easiness_factor)
        review.repetitions += 1

    review.easiness_factor = max(
        1.3,
        review.easiness_factor + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02),
    )

    now = datetime.now(timezone.utc)
    review.last_reviewed_at = now
    review.next_review_at = now + timedelta(days=review.interval)


class ReviewService:
    def __init__(self, uow: AbstractUoW) -> None:
        self._uow = uow

    async def get_due_cards(self, user_id: uuid.UUID) -> list[ReviewRead]:
        now = datetime.now(timezone.utc)
        async with self._uow as uow:
            reviews = await uow.reviews.list_due(user_id, now)
        return [ReviewRead.model_validate(r) for r in reviews]

    async def submit_review(self, user_id: uuid.UUID, card_id: uuid.UUID, quality: int) -> ReviewRead:
        if quality not in range(6):
            raise ValueError("Quality must be between 0 and 5")

        async with self._uow as uow:
            card = await uow.cards.get(card_id)
            if not card:
                raise NotFoundError("Card not found")

            review = await uow.reviews.get_by_user_and_card(user_id, card_id)
            if not review:
                review = Review(
                    user_id=user_id,
                    card_id=card_id,
                    easiness_factor=2.5,
                    interval=0,
                    repetitions=0,
                )
                await uow.reviews.add(review)

            _apply_sm2(review, quality)

        return ReviewRead.model_validate(review)
