import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.core.deps import get_current_user, get_uow
from src.schemas.card import CardRead
from src.schemas.deck import DeckCreate, DeckRead, DeckUpdate
from src.schemas.review import DeckStats
from src.schemas.user import UserRead
from src.services.deck import DeckService
from src.services.review import ReviewService
from src.uow.sqlalchemy import SQLAlchemyUoW

router = APIRouter(prefix="/decks", tags=["decks"])


@router.post("", response_model=DeckRead, status_code=201)
async def create_deck(
    data: DeckCreate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> DeckRead:
    return await DeckService(uow).create(data, owner_id=current_user.id)


@router.get("", response_model=list[DeckRead])
async def list_decks(
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> list[DeckRead]:
    return await DeckService(uow).list_for_user(current_user.id)


@router.get("/{deck_id}", response_model=DeckRead)
async def get_deck(
    deck_id: uuid.UUID,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> DeckRead:
    return await DeckService(uow).get(deck_id, user_id=current_user.id)


@router.patch("/{deck_id}", response_model=DeckRead)
async def update_deck(
    deck_id: uuid.UUID,
    data: DeckUpdate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> DeckRead:
    return await DeckService(uow).update(deck_id, data, user_id=current_user.id)


@router.delete("/{deck_id}", status_code=204)
async def delete_deck(
    deck_id: uuid.UUID,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> None:
    await DeckService(uow).delete(deck_id, user_id=current_user.id)


@router.get("/{deck_id}/stats", response_model=DeckStats)
async def get_deck_stats(
    deck_id: uuid.UUID,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> DeckStats:
    return await ReviewService(uow).get_deck_stats(current_user.id, deck_id)
