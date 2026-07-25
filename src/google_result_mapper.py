import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)

COMPETITION_NAME_MAP = {
    "UNSPECIFIED": "未知",
    "UNKNOWN": "未知",
    "LOW": "低",
    "MEDIUM": "中",
    "HIGH": "高",
}


def micros_to_twd(micros):
    if micros is None or micros <= 0:
        return None
    return round(micros / 1_000_000, 2)


def map_competition(enum_val):
    name = enum_val.name if hasattr(enum_val, "name") else str(enum_val)
    return COMPETITION_NAME_MAP.get(name, "未知")


def extract_monthly_searches(metrics):
    monthly = {}
    if metrics and metrics.monthly_search_volumes:
        for ms in metrics.monthly_search_volumes:
            key = f"{ms.year}-{ms.month + 1:02d}"
            monthly[key] = ms.monthly_searches
    return monthly


def _match_seed(text, seed_keywords):
    text_lower = text.lower()
    best = None
    best_len = 0
    for seed in seed_keywords:
        s = seed.lower()
        if s in text_lower or text_lower in s:
            if len(s) > best_len:
                best = seed
                best_len = len(s)
    return best if best else "綜合"


def results_to_dataframe(results, seed_keywords, query_info=None):
    rows = []

    for idea in results:
        text = idea.text
        metrics = idea.keyword_idea_metrics
        if not metrics:
            rows.append({
                "原始關鍵字": text,
                "標準化關鍵字": text,
                "來源種子詞": _match_seed(text, seed_keywords),
            })
            continue

        monthly = extract_monthly_searches(metrics)

        row = {
            "原始關鍵字": text,
            "標準化關鍵字": text,
            "來源種子詞": _match_seed(text, seed_keywords),
            "平均每月搜尋量": metrics.avg_monthly_searches,
            "競爭程度": map_competition(metrics.competition),
            "競爭指數": metrics.competition_index,
            "頁首出價低": micros_to_twd(metrics.low_top_of_page_bid_micros),
            "頁首出價高": micros_to_twd(metrics.high_top_of_page_bid_micros),
            "幣別": "TWD",
        }
        for k, v in monthly.items():
            row[k] = v
        rows.append(row)

    df = pd.DataFrame(rows)

    df["查詢地區"] = (query_info or {}).get("geo", "台灣")
    df["查詢語言"] = (query_info or {}).get("language", "中文 (繁體)")
    df["查詢時間"] = (query_info or {}).get("query_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    logger.info(f"轉換 {len(df)} 筆 API 結果為 DataFrame")
    return df
