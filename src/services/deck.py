import uuid

from src.core.exceptions import NotFoundError, ForbiddenError
from src.db.models.deck import Deck
from src.schemas.deck import DeckCreate, DeckUpdate, DeckRead
from src.uow.base import AbstractUoW


class DeckService:
    def __init__(self, uow: AbstractUoW) -> None:
        self._uow = uow

    async def create(self, data: DeckCreate, owner_id: uuid.UUID) -> DeckRead:
        async with self._uow as uow:
            deck = Deck(**data.model_dump(), owner_id=owner_id, is_system=False)
            await uow.decks.add(deck)
        return DeckRead.model_validate(deck)

    async def get(self, deck_id: uuid.UUID, user_id: uuid.UUID) -> DeckRead:
        async with self._uow as uow:
            deck = await uow.decks.get(deck_id)
        if not deck:
            raise NotFoundError("Deck not found")
        if not deck.is_system and deck.owner_id != user_id:
            raise ForbiddenError()
        return DeckRead.model_validate(deck)

    async def list_for_user(self, user_id: uuid.UUID) -> list[DeckRead]:
        """Возвращает системные деки + личные деки пользователя."""
        async with self._uow as uow:
            decks = await uow.decks.list_for_user(user_id)
        return [DeckRead.model_validate(d) for d in decks]

    async def update(self, deck_id: uuid.UUID, data: DeckUpdate, user_id: uuid.UUID) -> DeckRead:
        async with self._uow as uow:
            deck = await uow.decks.get(deck_id)
            if not deck:
                raise NotFoundError("Deck not found")
            if deck.is_system:
                raise ForbiddenError()
            if deck.owner_id != user_id:
                raise ForbiddenError()
            for field, value in data.model_dump(exclude_none=True).items():
                setattr(deck, field, value)
        return DeckRead.model_validate(deck)

    async def delete(self, deck_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with self._uow as uow:
            deck = await uow.decks.get(deck_id)
            if not deck:
                raise NotFoundError("Deck not found")
            if deck.is_system:
                raise ForbiddenError()
            if deck.owner_id != user_id:
                raise ForbiddenError()
            await uow.decks.delete(deck)
