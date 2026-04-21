import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base, uuid_pk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.user import User
    from src.db.models.card import Card


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Review(Base):
    """Хранит SM-2 прогресс конкретного пользователя по конкретной карточке."""

    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", name="uq_review_user_card"),
    )

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    card_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # SM-2 поля
    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5, nullable=False)
    interval: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # дней
    repetitions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    last_reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_review_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, nullable=False, index=True
    )

    user: Mapped["User"] = relationship("User", back_populates="reviews", lazy="noload")
    card: Mapped["Card"] = relationship("Card", back_populates="reviews", lazy="noload")
