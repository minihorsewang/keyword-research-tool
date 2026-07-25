import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_keywords_from_file(filepath):
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"找不到關鍵字檔案：{filepath}")
    with open(filepath, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
    keywords = []
    for line in lines:
        kw = line.strip()
        if kw:
            keywords.append(kw)
    logger.info(f"從檔案讀取 {len(keywords)} 個種子關鍵字: {filepath}")
    return keywords


def load_keywords_from_cli(keywords_str):
    parts = [k.strip() for k in keywords_str.split(",")]
    keywords = [k for k in parts if k]
    logger.info(f"從命令列讀取 {len(keywords)} 個種子關鍵字")
    return keywords


def clean_and_deduplicate(keywords):
    seen = set()
    cleaned = []
    for kw in keywords:
        norm = kw.strip().lower()
        norm = " ".join(norm.split())
        if norm and norm not in seen:
            seen.add(norm)
            cleaned.append(norm)
    logger.info(f"種子關鍵字清理後: {len(cleaned)} 個 (原始 {len(keywords)} 個)")
    return cleaned


def resolve_seed_keywords(cli_keywords=None):
    if cli_keywords:
        raw = load_keywords_from_cli(cli_keywords)
    else:
        from src.utils import INPUT_DIR
        txt_path = INPUT_DIR / "keywords.txt"
        if txt_path.exists():
            raw = load_keywords_from_file(txt_path)
        else:
            raise FileNotFoundError(
                "請提供種子關鍵字：\n"
                f"  1. 在 {INPUT_DIR / 'keywords.txt'} 每行放一個關鍵字\n"
                "  2. 或使用 --keywords \"貼紙印刷,標籤印刷\""
            )
    cleaned = clean_and_deduplicate(raw)
    if not cleaned:
        raise ValueError("沒有有效的種子關鍵字")
    return cleaned
