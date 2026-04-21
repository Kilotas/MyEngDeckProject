import uuid

from sqlalchemy import select

from src.db.models.card import Card
from src.repositories.base import SQLAlchemyRepository


class CardRepository(SQLAlchemyRepository[Card]):
    model = Card

    async def list_by_deck(self, deck_id: uuid.UUID) -> list[Card]:
        result = await self._session.execute(
            select(Card).where(Card.deck_id == deck_id)
        )
        return list(result.scalars().all())
