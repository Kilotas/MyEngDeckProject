"""Загрузка списка слов из файла."""

import sys
from pathlib import Path

WORDS_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "words.txt"


def load_words(limit: int) -> list[str]:
    if not WORDS_FILE.exists():
        print(f"ERROR: файл {WORDS_FILE} не найден.")
        print("Скачай google-10000-english-no-swears.txt и сохрани как data/words.txt")
        sys.exit(1)
    lines = WORDS_FILE.read_text(encoding="utf-8").splitlines()
    return [w.strip() for w in lines if w.strip()][:limit]
