import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.db.models.deck import Deck
    from src.db.models.review import Review


class Card(Base, TimestampMixin):
    __tablename__ = "cards"

    id: Mapped[uuid.UUID] = uuid_pk()
    word: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    translation: Mapped[str] = mapped_column(String(255), nullable=False)
    example: Mapped[str | None] = mapped_column(Text, nullable=True)
    audio_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    deck_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("decks.id", ondelete="CASCADE"), nullable=False, index=True
    )

    deck: Mapped["Deck"] = relationship("Deck", back_populates="cards", lazy="noload")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="card", lazy="noload")
