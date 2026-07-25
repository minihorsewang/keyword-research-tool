import logging

import pandas as pd

logger = logging.getLogger(__name__)

COMPETITION_NAME_MAP = {
    "UNSPECIFIED": "未知",
    "UNKNOWN": "未知",
    "LOW": "低",
    "MEDIUM": "中",
    "HIGH": "高",
}

MONTH_MAP = {
    0: "1", 1: "2", 2: "3", 3: "4", 4: "5", 5: "6",
    6: "7", 7: "8", 8: "9", 9: "10", 10: "11", 11: "12",
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
            key = f"{ms.year}-{MONTH_MAP.get(ms.month, str(ms.month))}"
            monthly[key] = ms.monthly_searches
    return monthly


def results_to_dataframe(results, seed_keywords):
    rows = []

    for idea in results:
        text = idea.text
        metrics = idea.keyword_idea_metrics
        if not metrics:
            rows.append({
                "原始關鍵字": text,
                "標準化關鍵字": text,
            })
            continue

        monthly = extract_monthly_searches(metrics)

        row = {
            "原始關鍵字": text,
            "標準化關鍵字": text,
            "平均每月搜尋量": metrics.avg_monthly_searches if metrics.avg_monthly_searches > 0 else None,
            "競爭程度": map_competition(metrics.competition),
            "競爭指數": metrics.competition_index if metrics.competition_index > 0 else None,
            "頁首出價低": micros_to_twd(metrics.low_top_of_page_bid_micros),
            "頁首出價高": micros_to_twd(metrics.high_top_of_page_bid_micros),
            "幣別": "TWD",
        }
        for k, v in monthly.items():
            row[k] = v
        rows.append(row)

    df = pd.DataFrame(rows)
    logger.info(f"轉換 {len(df)} 筆 API 結果為 DataFrame")
    return df
