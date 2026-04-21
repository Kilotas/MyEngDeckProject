import uuid

from src.core.exceptions import NotFoundError, ForbiddenError
from src.db.models.card import Card
from src.schemas.card import CardCreate, CardUpdate, CardRead
from src.uow.base import AbstractUoW


class CardService:
    def __init__(self, uow: AbstractUoW) -> None:
        self._uow = uow

    async def create(self, data: CardCreate, deck_id: uuid.UUID, user_id: uuid.UUID) -> CardRead:
        async with self._uow as uow:
            deck = await uow.decks.get(deck_id)
            if not deck:
                raise NotFoundError("Deck not found")
            if deck.owner_id != user_id:
                raise ForbiddenError()
            card = Card(**data.model_dump(), deck_id=deck_id)
            await uow.cards.add(card)
        return CardRead.model_validate(card)

    async def list_by_deck(self, deck_id: uuid.UUID, user_id: uuid.UUID) -> list[CardRead]:
        async with self._uow as uow:
            deck = await uow.decks.get(deck_id)
            if not deck:
                raise NotFoundError("Deck not found")
            if not deck.is_system and deck.owner_id != user_id:
                raise ForbiddenError()
            cards = await uow.cards.list_by_deck(deck_id)
        return [CardRead.model_validate(c) for c in cards]

    async def update(self, card_id: uuid.UUID, data: CardUpdate, user_id: uuid.UUID) -> CardRead:
        async with self._uow as uow:
            card = await uow.cards.get(card_id)
            if not card:
                raise NotFoundError("Card not found")
            deck = await uow.decks.get(card.deck_id)
            if deck.owner_id != user_id:
                raise ForbiddenError()
            for field, value in data.model_dump(exclude_none=True).items():
                setattr(card, field, value)
        return CardRead.model_validate(card)

    async def delete(self, card_id: uuid.UUID, user_id: uuid.UUID) -> None:
        async with self._uow as uow:
            card = await uow.cards.get(card_id)
            if not card:
                raise NotFoundError("Card not found")
            deck = await uow.decks.get(card.deck_id)
            if deck.owner_id != user_id:
                raise ForbiddenError()
            await uow.cards.delete(card)
