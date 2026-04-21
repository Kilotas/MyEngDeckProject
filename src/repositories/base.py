from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.base import Base

Model = TypeVar("Model", bound=Base)


class AbstractRepository(ABC, Generic[Model]):
    @abstractmethod
    async def get(self, id: uuid.UUID) -> Model | None: ...

    @abstractmethod
    async def list(self) -> list[Model]: ...

    @abstractmethod
    async def add(self, obj: Model) -> Model: ...

    @abstractmethod
    async def delete(self, obj: Model) -> None: ...


class SQLAlchemyRepository(AbstractRepository[Model]):
    model: type[Model]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, id: uuid.UUID) -> Model | None:
        return await self._session.get(self.model, id)

    async def list(self) -> list[Model]:
        result = await self._session.execute(select(self.model))
        return list(result.scalars().all())

    async def add(self, obj: Model) -> Model:
        self._session.add(obj)
        return obj

    async def delete(self, obj: Model) -> None:
        await self._session.delete(obj)
