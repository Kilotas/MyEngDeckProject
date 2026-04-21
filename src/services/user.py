import uuid

import bcrypt

from src.core.exceptions import AlreadyExistsError, NotFoundError
from src.db.models.user import User
from src.schemas.user import UserCreate, UserRead
from src.uow.base import AbstractUoW


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


class UserService:
    def __init__(self, uow: AbstractUoW) -> None:
        self._uow = uow

    async def register(self, data: UserCreate) -> UserRead:
        async with self._uow as uow:
            if await uow.users.get_by_email(data.email):
                raise AlreadyExistsError("Email already registered")
            if await uow.users.get_by_username(data.username):
                raise AlreadyExistsError("Username already taken")

            user = User(
                email=data.email,
                username=data.username,
                hashed_password=_hash_password(data.password),
            )
            await uow.users.add(user)

        return UserRead.model_validate(user)

    async def get_by_id(self, user_id: uuid.UUID) -> UserRead:
        async with self._uow as uow:
            user = await uow.users.get(user_id)
        if not user:
            raise NotFoundError("User not found")
        return UserRead.model_validate(user)

    def verify_password(self, plain: str, hashed: str) -> bool:
        return _verify_password(plain, hashed)
