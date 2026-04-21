from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.deps import get_uow
from src.core.exceptions import UnauthorizedError
from src.core.security import create_access_token, create_refresh_token, decode_token
from src.schemas.token import RefreshRequest, TokenPair
from src.schemas.user import UserCreate, UserRead
from src.services.user import UserService
from src.uow.sqlalchemy import SQLAlchemyUoW

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    data: UserCreate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
) -> UserRead:
    return await UserService(uow).register(data)


@router.post("/login", response_model=TokenPair)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
) -> TokenPair:
    service = UserService(uow)

    async with uow as u:
        user = await u.users.get_by_username(form.username)

    if not user or not service.verify_password(form.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    return TokenPair(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh(body: RefreshRequest) -> TokenPair:
    try:
        user_id = decode_token(body.refresh_token, expected_type="refresh")
    except ValueError:
        raise UnauthorizedError("Invalid or expired refresh token")

    return TokenPair(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )
