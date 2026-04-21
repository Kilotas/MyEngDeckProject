from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.core.exceptions import UnauthorizedError
from src.core.security import decode_token
from src.db.session import async_session_factory
from src.schemas.user import UserRead
from src.services.user import UserService
from src.uow.sqlalchemy import SQLAlchemyUoW

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_uow() -> SQLAlchemyUoW:
    return SQLAlchemyUoW(async_session_factory)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
) -> UserRead:
    try:
        user_id = decode_token(token, expected_type="access")
    except ValueError:
        raise UnauthorizedError("Invalid or expired token")

    user = await UserService(uow).get_by_id(user_id)
    if not user:
        raise UnauthorizedError()
    return user
