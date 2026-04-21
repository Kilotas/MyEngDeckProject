import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base, TimestampMixin, uuid_pk

import enum

if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.card import Card


class DifficultyLevel(str, enum.Enum):
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"


class Deck(Base, TimestampMixin):
    __tablename__ = "decks"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    level: Mapped[DifficultyLevel] = mapped_column(
        SAEnum(DifficultyLevel, name="difficulty_level"), nullable=False
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )

    owner: Mapped["User"] = relationship("User", back_populates="decks", lazy="noload")
    cards: Mapped[list["Card"]] = relationship("Card", back_populates="deck", lazy="noload")
