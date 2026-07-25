import csv
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def detect_encoding(filepath):
    encodings = ["utf-8-sig", "utf-8", "big5", "cp950", "cp1252", "latin-1"]
    for enc in encodings:
        try:
            with open(filepath, "r", encoding=enc) as f:
                f.read(2000)
            logger.info(f"編碼辨識成功: {enc} - {filepath}")
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    logger.warning(f"無法辨識編碼，預設使用 utf-8: {filepath}")
    return "utf-8"


def detect_delimiter(filepath, encoding):
    with open(filepath, "r", encoding=encoding) as f:
        sample = f.read(5000)
    tab_count = sample.count("\t")
    comma_count = sample.count(",")
    return "\t" if tab_count > comma_count else ","


def resolve_columns(df, column_aliases):
    df_lower = {str(c).strip().lower(): c for c in df.columns}
    mapping = {}
    for std_name, aliases in column_aliases.items():
        for alias in aliases:
            alias_lower = alias.strip().lower()
            if alias_lower in df_lower:
                mapping[std_name] = df_lower[alias_lower]
                break
    return mapping


def load_csv(filepath, column_aliases):
    filepath = Path(filepath)
    logger.info(f"開始讀取檔案: {filepath}")

    if not filepath.exists():
        raise FileNotFoundError(f"找不到檔案：{filepath}")

    if filepath.stat().st_size == 0:
        raise ValueError(f"檔案為空白：{filepath}")

    encoding = detect_encoding(filepath)
    delimiter = detect_delimiter(filepath, encoding)

    tab_char = "\t"
    logger.info(f"分隔符號: {'Tab' if delimiter == tab_char else '逗號'}")

    try:
        df = pd.read_csv(filepath, encoding=encoding, delimiter=delimiter, dtype=str)
    except Exception as e:
        raise ValueError(f"讀取 CSV 失敗：{e}")

    if df.empty:
        raise ValueError(f"檔案中沒有資料：{filepath}")

    logger.info(f"原始欄位: {list(df.columns)}")
    df.columns = [str(c).strip() for c in df.columns]

    mapping = resolve_columns(df, column_aliases)
    logger.info(f"欄位對應結果: {mapping}")

    if "keyword" not in mapping:
        raise ValueError("找不到「關鍵字」欄位，請確認此檔案是否由 Google Keyword Planner 匯出。")

    std_df = pd.DataFrame()
    std_df["原始關鍵字"] = df[mapping["keyword"]]

    field_map = {
        "avg_monthly_searches": "平均每月搜尋量",
        "competition": "競爭程度",
        "competition_index": "競爭指數",
        "top_of_page_bid_low": "頁首出價低",
        "top_of_page_bid_high": "頁首出價高",
        "three_month_change": "三個月變化",
        "yoy_change": "年增率",
        "currency": "幣別",
    }

    for std_key, cn_name in field_map.items():
        if std_key in mapping:
            std_df[cn_name] = df[mapping[std_key]]
        else:
            std_df[cn_name] = None

    std_df["原始欄位"] = str(list(df.columns))
    logger.info(f"成功載入 {len(std_df)} 筆資料")
    return std_df
