import uuid
from datetime import datetime, date

from sqlalchemy import select, func, case

from src.db.models.review import Review
from src.db.models.card import Card
from src.repositories.base import SQLAlchemyRepository


class ReviewRepository(SQLAlchemyRepository[Review]):
    model = Review

    async def get_by_user_and_card(self, user_id: uuid.UUID, card_id: uuid.UUID) -> Review | None:
        result = await self._session.execute(
            select(Review).where(Review.user_id == user_id, Review.card_id == card_id)
        )
        return result.scalar_one_or_none()

    async def list_due(self, user_id: uuid.UUID, now: datetime) -> list[Review]:
        result = await self._session.execute(
            select(Review).where(
                Review.user_id == user_id,
                Review.next_review_at <= now,
            )
        )
        return list(result.scalars().all())

    async def count_introduced_today(self, user_id: uuid.UUID, deck_id: uuid.UUID, today: date) -> int:
        result = await self._session.execute(
            select(func.count(Review.id))
            .join(Card, Review.card_id == Card.id)
            .where(
                Review.user_id == user_id,
                Card.deck_id == deck_id,
                Review.introduced_date == today,
            )
        )
        return result.scalar_one() or 0

    async def list_new_cards_for_deck(self, user_id: uuid.UUID, deck_id: uuid.UUID, limit: int) -> list[Card]:
        reviewed_subq = select(Review.card_id).where(Review.user_id == user_id)
        result = await self._session.execute(
            select(Card)
            .where(Card.deck_id == deck_id, Card.id.not_in(reviewed_subq))
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_due_for_deck(self, user_id: uuid.UUID, deck_id: uuid.UUID, now: datetime) -> list[Card]:
        result = await self._session.execute(
            select(Card)
            .join(Review, (Review.card_id == Card.id) & (Review.user_id == user_id))
            .where(Card.deck_id == deck_id, Review.next_review_at <= now)
        )
        return list(result.scalars().all())

    async def get_deck_stats(self, user_id: uuid.UUID, deck_id: uuid.UUID, now: datetime) -> dict:
        result = await self._session.execute(
            select(
                func.count(Card.id).label("total_cards"),
                func.count(Review.id).label("reviewed_cards"),
                func.count(case((Review.next_review_at <= now, Review.id))).label("due_cards"),
                func.count(case((Review.repetitions >= 5, Review.id))).label("learned_cards"),
                func.avg(case((Review.id.is_not(None), Review.interval))).label("avg_interval"),
            )
            .select_from(Card)
            .outerjoin(
                Review,
                (Review.card_id == Card.id) & (Review.user_id == user_id),
            )
            .where(Card.deck_id == deck_id)
        )
        row = result.one()
        total = row.total_cards or 0
        reviewed = row.reviewed_cards or 0
        return {
            "total_cards": total,
            "reviewed_cards": reviewed,
            "due_cards": row.due_cards or 0,
            "learned_cards": row.learned_cards or 0,
            "avg_interval": round(float(row.avg_interval or 0), 1),
            "new_cards": total - reviewed,
        }
