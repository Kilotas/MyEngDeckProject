import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base, TimestampMixin, uuid_pk

if TYPE_CHECKING:
    from src.db.models.deck import Deck
    from src.db.models.review import Review


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    daily_new_limit: Mapped[int] = mapped_column(Integer, default=20, nullable=False, server_default="20")

    decks: Mapped[list["Deck"]] = relationship("Deck", back_populates="owner", lazy="noload")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user", lazy="noload")
