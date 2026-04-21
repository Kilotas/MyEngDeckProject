"""
Seed скрипт: загружает 5000 английских слов с переводами и аудио.

Требования:
  - data/words.txt  (google-10000-english-no-swears.txt, один словом на строку)
  - MinIO запущен в Docker (localhost:9000)
  - PostgreSQL запущен в Docker (localhost:5432)

Использование:
  python -X utf8 scripts/seed_words.py              # все 5000 слов
  python -X utf8 scripts/seed_words.py --limit 50   # первые 50 (для теста)
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.seed.audio import upload_audio
from scripts.seed.db import get_level, insert_cards, setup_decks
from scripts.seed.translator import load_cache, translate_all
from scripts.seed.words import load_words

BATCH_SIZE        = 50  # слов за одну транзакцию в БД
AUDIO_CONCURRENCY = 5   # параллельных генераций аудио


async def main(limit: int) -> None:
    # Фаза 1: список слов
    words = load_words(limit)
    print(f"Слов загружено: {len(words)}")

    # Фаза 2: переводы (кешируются в data/translations_cache.json)
    cache = load_cache()
    cache = await translate_all(words, cache)

    # Фаза 3: пользователь + деки + уже существующие слова
    print("\nФаза 2: подготовка системных деков...")
    deck_ids, existing = await setup_decks()
    for level, words_set in existing.items():
        print(f"  {level.value}: {len(words_set)} слов уже в БД")

    # Фаза 4: аудио (edge-tts → MinIO) + запись в БД батчами
    print(f"\nФаза 3: аудио + запись в БД батчами по {BATCH_SIZE}...")
    sem = asyncio.Semaphore(AUDIO_CONCURRENCY)
    total_created = 0
    total_skipped = 0

    for batch_start in range(0, len(words), BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, len(words))
        batch = [(idx, words[idx]) for idx in range(batch_start, batch_end)]

        # Пропускаем слова которые уже есть в БД
        to_process = [
            (idx, word) for idx, word in batch
            if word not in existing[get_level(idx)]
        ]
        total_skipped += len(batch) - len(to_process)

        if not to_process:
            continue

        # Параллельная генерация и загрузка аудио
        audio_paths = await asyncio.gather(*[upload_audio(sem, word) for _, word in to_process])

        # Запись в БД
        await insert_cards(deck_ids, to_process, audio_paths, cache)

        # Обновляем локальный список уже существующих (чтобы не дублировать в следующих батчах)
        for idx, word in to_process:
            existing[get_level(idx)].add(word)
        total_created += len(to_process)

        pct = batch_end / len(words) * 100
        print(f"  [{pct:5.1f}%] +{len(to_process)} карточек | итого: {total_created} создано, {total_skipped} пропущено")

    print(f"\nГотово! {total_created} карточек создано, {total_skipped} пропущено.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed English words into Reword")
    parser.add_argument("--limit", type=int, default=5000, help="Сколько слов обработать (по умолчанию: 5000)")
    args = parser.parse_args()
    asyncio.run(main(args.limit))
