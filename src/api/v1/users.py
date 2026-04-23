from typing import Annotated

from fastapi import APIRouter, Depends

from src.core.deps import get_current_user, get_uow
from src.schemas.user import UserRead, UserUpdate
from src.services.user import UserService
from src.uow.sqlalchemy import SQLAlchemyUoW

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def get_me(
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    return current_user


@router.patch("/me", response_model=UserRead)
async def update_me(
    data: UserUpdate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> UserRead:
    return await UserService(uow).update_settings(current_user.id, data)
