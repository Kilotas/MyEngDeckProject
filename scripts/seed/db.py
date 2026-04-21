"""Работа с БД: пользователь, деки, карточки."""

import uuid

from sqlalchemy import select

from src.db.models.card import Card
from src.db.models.deck import Deck, DifficultyLevel
from src.db.session import async_session_factory

SEED_EMAIL    = "seed@reword.app"
SEED_USERNAME = "seed"
SEED_PASSWORD = "seedpassword123"

# Разбивка слов по уровням по частоте (индекс в общем списке)
LEVEL_RANGES = [
    (0,    1000, DifficultyLevel.beginner),
    (1000, 3000, DifficultyLevel.intermediate),
    (3000, 5000, DifficultyLevel.advanced),
]

DECK_NAMES = {
    DifficultyLevel.beginner:     "English — Beginner (1–1000)",
    DifficultyLevel.intermediate: "English — Intermediate (1001–3000)",
    DifficultyLevel.advanced:     "English — Advanced (3001–5000)",
}


def get_level(idx: int) -> DifficultyLevel:
    for start, end, level in LEVEL_RANGES:
        if start <= idx < end:
            return level
    return DifficultyLevel.advanced


async def _get_or_create_deck(session, level: DifficultyLevel) -> Deck:
    result = await session.execute(
        select(Deck).where(Deck.is_system == True, Deck.level == level)  # noqa: E712
    )
    deck = result.scalar_one_or_none()
    if not deck:
        deck = Deck(name=DECK_NAMES[level], level=level, is_system=True, owner_id=None)
        session.add(deck)
        await session.flush()
    return deck


async def setup_decks() -> tuple[dict[DifficultyLevel, uuid.UUID], dict[DifficultyLevel, set[str]]]:
    """
    Создаёт 3 системных дека (если не существуют).
    Возвращает: deck_ids и existing_words (слова уже в БД — для пропуска).
    """
    async with async_session_factory() as session:
        async with session.begin():
            deck_ids: dict[DifficultyLevel, uuid.UUID] = {}
            existing: dict[DifficultyLevel, set[str]] = {}

            for _, _, level in LEVEL_RANGES:
                deck = await _get_or_create_deck(session, level)
                deck_ids[level] = deck.id

                result = await session.execute(
                    select(Card.word).where(Card.deck_id == deck.id)
                )
                existing[level] = {row[0] for row in result.all()}

    return deck_ids, existing


async def insert_cards(
    deck_ids: dict[DifficultyLevel, uuid.UUID],
    batch: list[tuple[int, str]],        # [(word_index, word), ...]
    audio_paths: list[str | None],
    cache: dict[str, str],
) -> None:
    """Записывает батч карточек в БД одной транзакцией."""
    async with async_session_factory() as session:
        async with session.begin():
            for (idx, word), audio_path in zip(batch, audio_paths):
                level = get_level(idx)
                session.add(Card(
                    word=word,
                    translation=cache.get(word, word),
                    audio_path=audio_path,
                    deck_id=deck_ids[level],
                ))
