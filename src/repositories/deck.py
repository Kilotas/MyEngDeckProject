import uuid

from sqlalchemy import select

from src.db.models.deck import Deck
from src.repositories.base import SQLAlchemyRepository


class DeckRepository(SQLAlchemyRepository[Deck]):
    model = Deck

    async def list_for_user(self, user_id: uuid.UUID) -> list[Deck]:
        """Возвращает системные деки + личные деки пользователя."""
        result = await self._session.execute(
            select(Deck).where(
                (Deck.is_system == True) | (Deck.owner_id == user_id)  # noqa: E712
            )
        )
        return list(result.scalars().all())
