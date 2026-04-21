import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from src.core.deps import get_current_user, get_uow
from src.schemas.review import ReviewRead
from src.schemas.user import UserRead
from src.services.review import ReviewService
from src.uow.sqlalchemy import SQLAlchemyUoW

router = APIRouter(prefix="/reviews", tags=["reviews"])


class SubmitReviewRequest(BaseModel):
    card_id: uuid.UUID
    quality: int

    @field_validator("quality")
    @classmethod
    def validate_quality(cls, v: int) -> int:
        if v not in range(6):
            raise ValueError("quality must be between 0 and 5")
        return v


@router.get("/due", response_model=list[ReviewRead])
async def get_due_cards(
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> list[ReviewRead]:
    return await ReviewService(uow).get_due_cards(current_user.id)


@router.post("", response_model=ReviewRead)
async def submit_review(
    data: SubmitReviewRequest,
    uow: Annotated[SQLAlchemyUoW, Depends(get_uow)],
    current_user: Annotated[UserRead, Depends(get_current_user)],
) -> ReviewRead:
    return await ReviewService(uow).submit_review(
        user_id=current_user.id,
        card_id=data.card_id,
        quality=data.quality,
    )
