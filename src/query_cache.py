import hashlib
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_TTL_HOURS = 24


def _hash_keywords(keywords):
    raw = ",".join(sorted(kw.strip().lower() for kw in keywords))
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_path(cache_key):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{cache_key}.json"


def get_cached(keywords):
    cache_key = _hash_keywords(keywords)
    path = _cache_path(cache_key)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cached_time = datetime.fromisoformat(data["cached_at"])
        if datetime.now() - cached_time > timedelta(hours=CACHE_TTL_HOURS):
            logger.info(f"快取已過期: {cache_key}")
            return None
        logger.info(f"使用快取資料: {cache_key}")
        return data["results"]
    except (json.JSONDecodeError, KeyError, ValueError):
        return None


def save_cache(keywords, results):
    cache_key = _hash_keywords(keywords)
    path = _cache_path(cache_key)
    data = {
        "cached_at": datetime.now().isoformat(),
        "seed_keywords": keywords,
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"快取已儲存: {cache_key}")
