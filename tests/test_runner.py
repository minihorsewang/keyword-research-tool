"""
測試執行腳本
執行方式: python tests/test_runner.py
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.csv_loader import load_csv, detect_encoding, resolve_columns, detect_delimiter
from src.data_cleaner import clean_data, normalize_keyword, find_similar
from src.classifier import classify, classify_category, classify_intent, detect_region
from src.scorer import score
from src.keyword_cluster import cluster_keywords
from src.utils import load_json, safe_int, safe_float
import pandas as pd


def setup():
    global column_aliases, categories, intent_rules, business_rules
    column_aliases = load_json("column_aliases.json")
    categories = load_json("categories.json")
    intent_rules = load_json("intent_rules.json")
    business_rules = load_json("business_rules.json")


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test_utf8_csv():
    print("=== 1. UTF-8 CSV ===")
    df = load_csv(os.path.join(DATA_DIR, "test_utf8.csv"), column_aliases)
    assert len(df) > 0
    assert "原始關鍵字" in df.columns
    print(f"  PASS: 讀取 {len(df)} 筆資料")
    return df


def test_chinese_columns():
    print("=== 2. 中文欄位名稱 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_chinese_columns.csv"), column_aliases)
    assert len(df) > 0
    assert "原始關鍵字" in df.columns
    print(f"  PASS: 中文字段辨識成功，讀取 {len(df)} 筆")


def test_big5_csv():
    print("=== 3. Big5 CSV ===")
    df = load_csv(os.path.join(DATA_DIR, "test_big5.csv"), column_aliases)
    assert len(df) > 0
    print(f"  PASS: Big5 編碼讀取成功，讀取 {len(df)} 筆")


def test_missing_column():
    print("=== 4. 缺少必要欄位 ===")
    try:
        load_csv(os.path.join(DATA_DIR, "test_missing_column.csv"), column_aliases)
        assert False, "應該拋出 ValueError"
    except ValueError as e:
        assert "關鍵字" in str(e)
        print(f"  PASS: 正確拋出錯誤: {e}")


def test_thousands():
    print("=== 5. 千分位數字 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_thousands.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    first = cleaned.iloc[0]
    assert safe_int(first["平均每月搜尋量"]) == 1200
    print("  PASS: 千分位數字處理正確")


def test_less_than_10():
    print("=== 6. < 10 搜尋量 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_less_than_10.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    first = cleaned.iloc[0]
    val = safe_int(first["平均每月搜尋量"])
    assert val == 5 or val == 0
    print(f"  PASS: < 10 處理正確 (值: {val})")


def test_competition_lang():
    print("=== 7. 競爭程度中英文 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_chinese_columns.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    classified = classify(cleaned, categories, intent_rules)
    result = score(classified, business_rules)
    assert "競爭難度" in result.columns
    print(f"  PASS: 競爭程度辨識成功")


def test_duplicates():
    print("=== 8. 完全重複關鍵字 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_duplicates.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    duplicates = cleaned[cleaned["是否高度相似"]]
    assert len(cleaned) < len(df)
    print(f"  PASS: 原始 {len(df)} 筆 -> 有效 {len(cleaned)} 筆 (含相似)")


def test_normalize():
    print("=== 9. 標準化函數 ===")
    assert normalize_keyword("貼紙 印刷") == "貼紙 印刷"
    assert normalize_keyword("貼紙印刷") == "貼紙印刷"
    assert normalize_keyword("貼紙　印刷") == "貼紙 印刷"
    assert normalize_keyword("  HELLO  ") == "hello"
    print("  PASS: 標準化正確")


def test_irrelevant():
    print("=== 10. 無關關鍵字 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_irrelevant.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    result = classify(cleaned, categories, intent_rules)
    irrelevant = result[result["是否可能無關"]]
    assert len(irrelevant) > 0
    print(f"  PASS: 標記 {len(irrelevant)} 筆可能無關")


def test_empty_file():
    print("=== 11. 空白檔案 ===")
    try:
        load_csv(os.path.join(DATA_DIR, "test_empty.csv"), column_aliases)
        assert False, "應該拋出 ValueError"
    except ValueError:
        print("  PASS: 正確處理空白檔案")


def test_similar():
    print("=== 12. 高度相似關鍵字 ===")
    seen = set()
    t1, t2 = find_similar("貼紙印刷", seen)
    assert t1 is None
    seen.add("貼紙印刷")
    match, mtype = find_similar("貼紙 印刷", seen)
    assert match is not None
    print(f"  PASS: 高度相似辨識正確 ({mtype})")


def test_classifier():
    print("=== 13. 分類功能 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_utf8.csv"), column_aliases)
    cleaned, _, _ = clean_data(df)
    df_c = classify(cleaned, categories, intent_rules)
    assert "產品大類" in df_c.columns
    labels = df_c["產品大類"].value_counts()
    print(f"  PASS: 分類完成，類別分布: {dict(labels)}")


def test_full_pipeline():
    print("=== 14. 完整流程測試 ===")
    df = load_csv(os.path.join(DATA_DIR, "test_utf8.csv"), column_aliases)
    df, _, _ = clean_data(df)
    df = classify(df, categories, intent_rules)
    df = score(df, business_rules)
    clusters = cluster_keywords(df, categories)
    assert len(clusters) > 0
    print(f"  PASS: 完整流程成功，分群數量: {len(clusters)}")


def test_large_data():
    print("=== 15. 大量資料測試 ===")
    rows = []
    for i in range(100):
        rows.append({"Keyword": f"貼紙印刷測試{i}", "Avg. monthly searches": str(100 + i), "Competition": "Low", "Competition index": "0.2"})
    df = pd.DataFrame(rows)
    column_aliases_local = {"keyword": ["keyword"], "avg_monthly_searches": ["avg. monthly searches"],
                            "competition": ["competition"], "competition_index": ["competition index"]}
    df["原始關鍵字"] = df["Keyword"]
    cleaned, _, _ = clean_data(df)
    assert len(cleaned) == 100
    print(f"  PASS: 100 筆資料處理成功")


def run_all_tests():
    passed = 0
    failed = 0
    tests = [
        ("UTF-8 CSV 讀取", test_utf8_csv),
        ("中文欄位名稱", test_chinese_columns),
        ("Big5 CSV", test_big5_csv),
        ("缺少必要欄位", test_missing_column),
        ("千分位數字", test_thousands),
        ("< 10 搜尋量", test_less_than_10),
        ("競爭程度中英文", test_competition_lang),
        ("完全重複關鍵字", test_duplicates),
        ("標準化函數", test_normalize),
        ("無關關鍵字", test_irrelevant),
        ("空白檔案", test_empty_file),
        ("高度相似", test_similar),
        ("分類功能", test_classifier),
        ("完整流程", test_full_pipeline),
        ("大量資料", test_large_data),
    ]

    for name, func in tests:
        try:
            func()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            traceback.print_exc()
            failed += 1
        print()

    print(f"={'='*40}=")
    print(f"測試結果: {passed} 通過, {failed} 失敗, 共 {len(tests)} 項")
    print(f"={'='*40}=")
    return failed == 0


if __name__ == "__main__":
    setup()
    success = run_all_tests()
    sys.exit(0 if success else 1)
