"""Перевод слов EN→RU с кешированием в JSON-файл."""

import asyncio
import json
from pathlib import Path

from deep_translator import GoogleTranslator

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CACHE_FILE = DATA_DIR / "translations_cache.json"

TRANSLATE_DELAY = 0.3  # пауза между запросами к Google (сек)


def load_cache() -> dict[str, str]:
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def save_cache(cache: dict[str, str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


def _translate_sync(word: str) -> str:
    """Синхронный перевод одного слова (запускается в thread pool)."""
    try:
        result = GoogleTranslator(source="en", target="ru").translate(word)
        return result or word
    except Exception:
        return word


async def translate_all(words: list[str], cache: dict[str, str]) -> dict[str, str]:
    """
    Переводит все слова которых нет в кеше.
    Сохраняет кеш каждые 100 слов — если прервать и запустить снова,
    продолжит с того же места.
    """
    missing = [w for w in words if w not in cache]
    if not missing:
        print(f"Все переводы уже в кеше ({len(cache)} слов).")
        return cache

    print(f"\nФаза 1: переводим {len(missing)} слов через Google Translate...")
    loop = asyncio.get_event_loop()

    for i, word in enumerate(missing, 1):
        cache[word] = await loop.run_in_executor(None, _translate_sync, word)
        if i % 100 == 0:
            save_cache(cache)
            print(f"  {i}/{len(missing)} переведено...")
        await asyncio.sleep(TRANSLATE_DELAY)

    save_cache(cache)
    print(f"Переводы готовы. Кеш сохранён в {CACHE_FILE.name}")
    return cache
