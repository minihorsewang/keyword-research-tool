import re
import logging
import unicodedata

logger = logging.getLogger(__name__)


def normalize_keyword(text):
    if not isinstance(text, str):
        return ""
    text = text.strip()
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"\s+", " ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9\u4e00-\u9fff\-\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def find_similar(normalized, seen):
    for existing in seen:
        if normalized == existing:
            return existing, "完全重複"
        if normalized in existing or existing in normalized:
            short, long = (normalized, existing) if len(normalized) <= len(existing) else (existing, normalized)
            if len(short) / len(long) >= 0.6:
                return existing, "高度相似"
        no_space_norm = normalized.replace(" ", "")
        no_space_exist = existing.replace(" ", "")
        if no_space_norm == no_space_exist:
            return existing, "高度相似"
        if no_space_norm and no_space_exist:
            if no_space_norm in no_space_exist or no_space_exist in no_space_norm:
                short_ns = min(no_space_norm, no_space_exist, key=len)
                long_ns = max(no_space_norm, no_space_exist, key=len)
                if len(short_ns) / len(long_ns) >= 0.6:
                    return existing, "高度相似"
    return None, None


def clean_data(df):
    logger.info("開始清理資料")
    total = len(df)
    df = df.copy()

    df["標準化關鍵字"] = df["原始關鍵字"].apply(normalize_keyword)
    df["標準化關鍵字"] = df["標準化關鍵字"].fillna("").astype(str)

    empty_mask = df["標準化關鍵字"] == ""
    empty_count = int(empty_mask.sum())
    df = df[~empty_mask]
    logger.info(f"移除 {empty_count} 筆空白關鍵字")

    seen = {}
    duplicate_flags = []
    similar_flags = []
    similar_with = []

    for norm in df["標準化關鍵字"]:
        if norm in seen:
            duplicate_flags.append(True)
            similar_flags.append(False)
            similar_with.append(seen[norm])
        else:
            match, match_type = find_similar(norm, set(seen.keys()))
            if match:
                duplicate_flags.append(False)
                similar_flags.append(True)
                similar_with.append(match)
            else:
                duplicate_flags.append(False)
                similar_flags.append(False)
                similar_with.append("")
            seen[norm] = norm

    df["是否完全重複"] = duplicate_flags
    df["是否高度相似"] = similar_flags
    df["相似對象"] = similar_with

    duplicate_count = int(sum(duplicate_flags))
    df_valid = df[~df["是否完全重複"]].copy()
    logger.info(f"原始: {total} 筆, 空白: {empty_count}, 完全重複: {duplicate_count}, "
                f"有效: {len(df_valid)} 筆, 高度相似: {sum(similar_flags)} 筆")
    return df_valid, empty_count, duplicate_count
