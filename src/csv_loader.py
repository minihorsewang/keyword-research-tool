import csv
import logging
import re
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def detect_encoding(filepath):
    encodings = ["utf-8-sig", "utf-8", "big5", "cp950", "cp1252", "latin-1"]
    raw_bytes = open(filepath, "rb").read(2000)
    for enc in encodings:
        try:
            decoded = raw_bytes.decode(enc)
            # 檢查是否包含中文字元
            has_chinese = any("\u4e00" <= ch <= "\u9fff" for ch in decoded)
            # 若檔案含有中文，但此編碼解不出中文，跳過
            if not has_chinese:
                # 檢查 raw_bytes 中是否有常見 UTF-8/Big5 中文字節特徵
                has_cjk_bytes = any(b > 0x7f for b in raw_bytes)
                if has_cjk_bytes and enc in ["cp1252", "latin-1"]:
                    continue
            logger.info(f"編碼辨識成功: {enc} - {filepath}")
            return enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    logger.warning(f"無法辨識編碼，預設使用 utf-8: {filepath}")
    return "utf-8"


def detect_delimiter(filepath, encoding):
    with open(filepath, "r", encoding=encoding) as f:
        first_line = f.readline()
    # 用 csv 模組 Sniffer 偵測
    try:
        dialect = csv.Sniffer().sniff(first_line)
        delimiter = dialect.delimiter
    except Exception:
        # 手動判斷
        tab_count = first_line.count("\t")
        comma_count = first_line.count(",")
        delimiter = "\t" if tab_count > comma_count else ","
    return delimiter


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
