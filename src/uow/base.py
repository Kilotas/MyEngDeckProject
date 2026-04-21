from abc import ABC, abstractmethod

from src.repositories.user import UserRepository
from src.repositories.deck import DeckRepository
from src.repositories.card import CardRepository
from src.repositories.review import ReviewRepository


class AbstractUoW(ABC):
    users: UserRepository
    decks: DeckRepository
    cards: CardRepository
    reviews: ReviewRepository

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "AbstractUoW":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
