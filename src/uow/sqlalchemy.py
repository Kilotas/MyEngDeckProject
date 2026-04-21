from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.repositories.user import UserRepository
from src.repositories.deck import DeckRepository
from src.repositories.card import CardRepository
from src.repositories.review import ReviewRepository
from src.uow.base import AbstractUoW


class SQLAlchemyUoW(AbstractUoW):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> "SQLAlchemyUoW":
        self._session: AsyncSession = self._session_factory()
        self.users = UserRepository(self._session)
        self.decks = DeckRepository(self._session)
        self.cards = CardRepository(self._session)
        self.reviews = ReviewRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await super().__aexit__(exc_type, exc_val, exc_tb)
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
