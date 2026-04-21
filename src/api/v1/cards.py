import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from src.core.deps import get_current_user, get_uow
from src.schemas.card import CardCreate, CardRead, CardUpdate
from src.schemas.user import UserRead
from src.services.card import CardService
from src.uow.sqlalchemy import SQLAlchemyUoW

router = APIRouter(prefix="/decks/{deck_id}/cards", tags=["cards"])


@router.post("", response_model=CardRead, status_code=201)
async def create_card(
    deck_id: uuid.UUID,
    data: CardCreate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> CardRead:
    return await CardService(uow).create(data, deck_id=deck_id, user_id=current_user.id)


@router.get("", response_model=list[CardRead])
async def list_cards(
    deck_id: uuid.UUID,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> list[CardRead]:
    return await CardService(uow).list_by_deck(deck_id, user_id=current_user.id)


@router.patch("/{card_id}", response_model=CardRead)
async def update_card(
    deck_id: uuid.UUID,
    card_id: uuid.UUID,
    data: CardUpdate,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> CardRead:
    return await CardService(uow).update(card_id, data, user_id=current_user.id)


@router.delete("/{card_id}", status_code=204)
async def delete_card(
    deck_id: uuid.UUID,
    card_id: uuid.UUID,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> None:
    await CardService(uow).delete(card_id, user_id=current_user.id)
