import sys
import logging
from pathlib import Path
from datetime import datetime

from src.csv_loader import load_csv
from src.data_cleaner import clean_data
from src.classifier import classify
from src.scorer import score
from src.keyword_cluster import cluster_keywords
from src.page_planner import plan_pages
from src.excel_exporter import export_excel
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


def main():
    logger = setup_logging()
    logger.info("=== 印刷關鍵字分析工具 開始執行 ===")

    try:
        # 載入設定檔
        logger.info("載入設定檔...")
        column_aliases = load_json("column_aliases.json")
        categories = load_json("categories.json")
        intent_rules = load_json("intent_rules.json")
        business_rules = load_json("business_rules.json")

        # 取得輸入檔案
        input_files = get_input_files()
        if not input_files:
            print("錯誤：找不到 CSV 檔案。請將 Keyword Planner 匯出的 CSV 放入 input 資料夾。")
            logger.error("找不到輸入檔案")
            sys.exit(1)

        input_file = input_files[0]
        print(f"讀取檔案：{input_file.name}")

        all_data = []
        for f in input_files:
            df = load_csv(f, column_aliases)
            all_data.append(df)

        import pandas as pd
        df = pd.concat(all_data, ignore_index=True)
        original_count = len(df)

        # 清理資料
        df_clean = clean_data(df)
        valid_count = len(df_clean)
        duplicate_count = original_count - valid_count

        # 分類
        df_classified = classify(df_clean, categories, intent_rules)
        irrelevant_count = df_classified["是否可能無關"].sum()

        # 評分
        df_scored = score(df_classified, business_rules)

        # 分群
        clusters = cluster_keywords(df_scored, categories)

        # 頁面規劃
        pages = plan_pages(clusters, df_scored)

        # 建立摘要資料
        high_count = int((df_scored["優先級"] == "高").sum())
        summary_data = {
            "原始關鍵字數": original_count,
            "有效關鍵字數": valid_count,
            "重複關鍵字數": duplicate_count,
            "可能無關數量": int(irrelevant_count),
            "高優先關鍵字數": high_count,
            "輸入檔案": input_file.name,
            "分析日期": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # 匯出 Excel
        output_path = export_excel(df_scored, clusters, pages, OUTPUT_DIR, summary_data)

        # 顯示結果
        print(f"\n分析完成")
        print(f"共處理：{original_count} 個關鍵字")
        print(f"有效關鍵字：{valid_count} 個")
        print(f"高優先關鍵字：{high_count} 個")
        print(f"報告位置：{output_path}")

        logger.info(f"分析完成，輸出檔案: {output_path}")
        logger.info("=== 執行結束 ===")

    except FileNotFoundError as e:
        print(f"錯誤：{e}")
        logger.error(f"檔案錯誤: {e}", exc_info=True)
        sys.exit(1)
    except ValueError as e:
        print(f"錯誤：{e}")
        logger.error(f"資料錯誤: {e}", exc_info=True)
        sys.exit(1)
    except Exception as e:
        print(f"執行失敗：{e}")
        logger.error(f"未預期錯誤: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
