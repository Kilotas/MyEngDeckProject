import uuid
from datetime import datetime

from sqlalchemy import select

from src.db.models.review import Review
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
