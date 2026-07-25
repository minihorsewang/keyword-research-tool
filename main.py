import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.csv_loader import load_csv
from src.data_cleaner import clean_data
from src.classifier import classify
from src.scorer import score
from src.keyword_cluster import cluster_keywords
from src.page_planner import plan_pages
from src.excel_exporter import export_excel, export_google_report
from src.override import load_overrides, apply_classify_overrides, apply_cluster_overrides
from src.keyword_input import resolve_seed_keywords
from src.google_ads_client import get_client, get_customer_id
from google.ads.googleads.errors import GoogleAdsException
from src.keyword_query import query_with_retry, format_google_ads_error
from src.google_result_mapper import results_to_dataframe
from src.query_cache import get_cached, save_cache
from src.utils import (
    load_json, ensure_dirs, get_input_files,
    CONFIG_DIR, INPUT_DIR, OUTPUT_DIR, LOGS_DIR
)


def setup_logging():
    ensure_dirs()
    log_file = LOGS_DIR / f"app_{datetime.now().strftime('%Y%m%d')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return logging.getLogger(__name__)


def run_csv_flow(logger):
    logger.info("執行 CSV 分析流程")
    column_aliases = load_json("column_aliases.json")

    input_files = get_input_files()
    if not input_files:
        print("錯誤：找不到 CSV 檔案。請將 Keyword Planner 匯出的 CSV 放入 input 資料夾。")
        sys.exit(1)

    all_data = []
    for f in input_files:
        df = load_csv(f, column_aliases)
        all_data.append(df)

    df = pd.concat(all_data, ignore_index=True)
    original_count = len(df)
    raw_df = df.copy()

    df_clean, empty_count, dup_count = clean_data(df)
    valid_count = len(df_clean)

    return df_clean, raw_df, {
        "source": "CSV",
        "original_count": original_count,
        "empty_count": empty_count,
        "dup_count": dup_count,
        "valid_count": valid_count,
        "input_files": [f.name for f in input_files],
    }


def run_google_flow(logger, cli_keywords, cli_customer_id=None):
    logger.info("執行 Google Ads API 查詢流程")
    seed_keywords = resolve_seed_keywords(cli_keywords)
    from_cache = False

    from src.keyword_query import CONFIG as QUERY_CONFIG
    query_info = {
        "query_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "geo": QUERY_CONFIG.get("geo_target_name", "台灣"),
        "language": QUERY_CONFIG.get("language_name", "中文 (繁體)"),
        "network": QUERY_CONFIG.get("keyword_plan_network", "Google Search"),
    }

    def _cache_ctx(cid=""):
        return {
            "customer_id": cid,
            "geo": query_info.get("geo", ""),
            "language": query_info.get("language", ""),
            "network": query_info.get("network", ""),
        }

    cached = get_cached(seed_keywords, **_cache_ctx())
    if cached is not None:
        df = pd.DataFrame(cached)
        from_cache = True
    else:
        client = get_client()
        customer_id = get_customer_id(client, cli_customer_id)
        logger.info(f"查詢帳戶 ID: {customer_id}")
        query_info["customer_id"] = customer_id
        results = query_with_retry(client, customer_id, seed_keywords)
        df = results_to_dataframe(results, seed_keywords, query_info)
        save_cache(seed_keywords, df.to_dict(orient="records"), **_cache_ctx(customer_id))

    avg_volume = ""
    if "平均每月搜尋量" in df.columns:
        vals = pd.to_numeric(df["平均每月搜尋量"], errors="coerce")
        avg_volume = f"{vals.mean():.0f}" if vals.notna().any() else ""

    query_info["customer_id"] = query_info.get("customer_id", "（快取）")
    query_info["from_cache"] = from_cache
    query_info["seed_keywords"] = seed_keywords
    query_info["avg_volume"] = avg_volume

    output_path = export_google_report(df, OUTPUT_DIR, query_info)

    print(f"\n查詢完成")
    print(f"資料來源：Google Ads API")
    print(f"種子關鍵字：{'、'.join(seed_keywords)}")
    print(f"建議關鍵字：{len(df)} 個")
    print(f"使用快取：{'是' if from_cache else '否'}")
    print(f"報告位置：{output_path}")
    logger.info(f"查詢完成，輸出檔案: {output_path}")


def run_analysis_pipeline(df_clean, raw_df, source_info, logger):
    categories = load_json("categories.json")
    intent_rules = load_json("intent_rules.json")
    business_rules = load_json("business_rules.json")

    df_classified = classify(df_clean, categories, intent_rules)
    irrelevant_count = int(df_classified["是否可能無關"].sum())

    classify_rules, cluster_rules = load_overrides(CONFIG_DIR, INPUT_DIR)
    df_classified = apply_classify_overrides(df_classified, classify_rules)

    df_scored = score(df_classified, business_rules)

    clusters = cluster_keywords(df_scored, categories)
    clusters = apply_cluster_overrides(clusters, df_scored, cluster_rules)

    pages = plan_pages(clusters, df_scored)

    high_count = int((df_scored["優先級"] == "高").sum())
    similar_count = int(df_clean["是否高度相似"].sum())

    if source_info["source"] == "CSV":
        input_label = "、".join(source_info["input_files"])
    else:
        input_label = "、".join(source_info["seed_keywords"])

    summary_data = {
        "資料來源": source_info["source"],
        "原始關鍵字數": source_info["original_count"],
        "空白關鍵字數": source_info["empty_count"],
        "完全重複關鍵字數": source_info["dup_count"],
        "高度相似關鍵字數": similar_count,
        "有效關鍵字數": source_info["valid_count"],
        "可能無關數量": irrelevant_count,
        "高優先關鍵字數": high_count,
        "輸入": input_label,
        "分析日期": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    output_path = export_excel(df_scored, clusters, pages, OUTPUT_DIR, summary_data, raw_df=raw_df)

    print(f"\n分析完成")
    print(f"資料來源：{source_info['source']}")
    print(f"原始資料：{source_info['original_count']} 筆")
    print(f"  空白關鍵字：{source_info['empty_count']} 筆")
    print(f"  完全重複：{source_info['dup_count']} 筆")
    print(f"  高度相似：{similar_count} 筆")
    print(f"有效關鍵字：{source_info['valid_count']} 筆")
    print(f"高優先關鍵字：{high_count} 個")
    print(f"報告位置：{output_path}")
    logger.info(f"分析完成，輸出檔案: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="台灣印刷關鍵字分析工具")
    parser.add_argument(
        "--source", choices=["csv", "google"], default="csv",
        help="資料來源：csv (Keyword Planner), google (Google Ads API)"
    )
    parser.add_argument(
        "--keywords",
        help="種子關鍵字，逗號分隔（僅 google 模式）"
    )
    parser.add_argument(
        "--customer-id",
        help="Google Ads 帳戶 ID（10 位數字，去掉橫線）"
    )
    return parser.parse_args()


def main():
    logger = setup_logging()
    args = parse_args()
    logger.info(f"=== 印刷關鍵字分析工具 開始執行（來源: {args.source}）===")

    try:
        if args.source == "google":
            run_google_flow(logger, args.keywords, args.customer_id)
        else:
            df_clean, raw_df, source_info = run_csv_flow(logger)
            run_analysis_pipeline(df_clean, raw_df, source_info, logger)
        logger.info("=== 執行結束 ===")

    except FileNotFoundError as e:
        print(f"錯誤：{e}")
        logger.error(f"檔案錯誤: {e}", exc_info=True)
        sys.exit(1)
    except ValueError as e:
        print(f"錯誤：{e}")
        logger.error(f"資料錯誤: {e}", exc_info=True)
        sys.exit(1)
    except GoogleAdsException as e:
        detail = format_google_ads_error(e)
        print(f"\nGoogle Ads API 錯誤：\n{detail}")
        logger.error(f"Google Ads API 錯誤:\n{detail}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        print(f"執行失敗：{e}")
        logger.error(f"未預期錯誤: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
