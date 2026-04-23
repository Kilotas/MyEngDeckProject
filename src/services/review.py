import uuid
from datetime import datetime, timezone, timedelta, date

from src.core.exceptions import NotFoundError
from src.db.models.review import Review
from src.schemas.card import CardRead
from src.schemas.review import ReviewRead, DeckStats
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

    async def get_learn_cards(self, user_id: uuid.UUID, deck_id: uuid.UUID) -> list[CardRead]:
        now = datetime.now(timezone.utc)
        today = now.date()
        async with self._uow as uow:
            user = await uow.users.get(user_id)
            daily_limit = user.daily_new_limit if user else 20
            introduced_today = await uow.reviews.count_introduced_today(user_id, deck_id, today)
            remaining = max(0, daily_limit - introduced_today)
            if remaining == 0:
                return []
            cards = await uow.reviews.list_new_cards_for_deck(user_id, deck_id, remaining)
        return [CardRead.model_validate(c) for c in cards]

    async def get_review_cards(self, user_id: uuid.UUID, deck_id: uuid.UUID) -> list[CardRead]:
        now = datetime.now(timezone.utc)
        async with self._uow as uow:
            cards = await uow.reviews.list_due_for_deck(user_id, deck_id, now)
        return [CardRead.model_validate(c) for c in cards]

    async def get_deck_stats(self, user_id: uuid.UUID, deck_id: uuid.UUID) -> DeckStats:
        now = datetime.now(timezone.utc)
        today = now.date()
        async with self._uow as uow:
            user = await uow.users.get(user_id)
            daily_limit = user.daily_new_limit if user else 20
            introduced_today = await uow.reviews.count_introduced_today(user_id, deck_id, today)
            data = await uow.reviews.get_deck_stats(user_id, deck_id, now)
        remaining = max(0, daily_limit - introduced_today)
        learn_available = min(remaining, data["new_cards"])
        return DeckStats(**data, learn_available=learn_available)

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
                    introduced_date=datetime.now(timezone.utc).date(),
                )
                await uow.reviews.add(review)

            _apply_sm2(review, quality)

        return ReviewRead.model_validate(review)
