import sys, os
from unittest.mock import MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.google_result_mapper import (
    map_competition, micros_to_twd, extract_monthly_searches, results_to_dataframe,
)


class FakeEnum:
    def __init__(self, name):
        self.name = name


class FakeMetrics:
    def __init__(self, avg=1000, comp="LOW", comp_idx=0.5,
                 low_bid=5000000, high_bid=15000000, monthly=None):
        self.avg_monthly_searches = avg
        self.competition = FakeEnum(comp)
        self.competition_index = comp_idx
        self.low_top_of_page_bid_micros = low_bid
        self.high_top_of_page_bid_micros = high_bid
        self.monthly_search_volumes = monthly or []


class FakeMonthlyVolume:
    def __init__(self, year, month, searches):
        self.year = year
        self.month = month
        self.monthly_searches = searches


class FakeIdea:
    def __init__(self, text, metrics=None):
        self.text = text
        self.keyword_idea_metrics = metrics


def test_map_competition_known():
    assert map_competition(FakeEnum("LOW")) == "低"
    assert map_competition(FakeEnum("MEDIUM")) == "中"
    assert map_competition(FakeEnum("HIGH")) == "高"
    print("  PASS: 競爭程度對映")


def test_map_competition_unknown():
    assert map_competition(FakeEnum("UNKNOWN")) == "未知"
    assert map_competition(FakeEnum("UNSPECIFIED")) == "未知"
    assert map_competition("SOME_STRING") == "未知"
    print("  PASS: 未知競爭程度回傳「未知」")


def test_micros_to_twd_normal():
    assert micros_to_twd(10_000_000) == 10.0
    assert micros_to_twd(12_345_678) == 12.35
    print("  PASS: 微元轉台幣")


def test_micros_to_twd_edge():
    assert micros_to_twd(None) is None
    assert micros_to_twd(0) is None
    assert micros_to_twd(-100) is None
    print("  PASS: 邊界值處理")


def test_extract_monthly_searches_empty():
    result = extract_monthly_searches(None)
    assert result == {}
    print("  PASS: 無月搜尋量回傳空 dict")


def test_extract_monthly_searches_with_data():
    volumes = [FakeMonthlyVolume(2026, 0, 500), FakeMonthlyVolume(2026, 6, 800)]
    metrics = FakeMetrics(monthly=volumes)
    result = extract_monthly_searches(metrics)
    assert result == {"2026-1": 500, "2026-7": 800}
    print("  PASS: 月搜尋量提取")


def test_results_to_dataframe_full():
    ideas = [
        FakeIdea("貼紙印刷", FakeMetrics()),
        FakeIdea("標籤印刷", FakeMetrics(avg=500, comp="HIGH", comp_idx=0.9)),
    ]
    df = results_to_dataframe(ideas, ["貼紙印刷"])
    assert len(df) == 2
    assert list(df["原始關鍵字"]) == ["貼紙印刷", "標籤印刷"]
    assert df.iloc[0]["平均每月搜尋量"] == 1000
    assert df.iloc[1]["競爭程度"] == "高"
    print("  PASS: 完整資料轉 DataFrame")


def test_results_to_dataframe_no_metrics():
    ideas = [FakeIdea("貼紙印刷", None)]
    df = results_to_dataframe(ideas, ["貼紙印刷"])
    assert len(df) == 1
    assert "平均每月搜尋量" not in df.columns
    print("  PASS: 無 metrics 仍可轉換")


def run_all_tests():
    passed = failed = 0
    tests = [
        ("競爭程度對映", test_map_competition_known),
        ("未知競爭程度", test_map_competition_unknown),
        ("微元轉台幣", test_micros_to_twd_normal),
        ("邊界值處理", test_micros_to_twd_edge),
        ("空月搜尋量", test_extract_monthly_searches_empty),
        ("月搜尋量提取", test_extract_monthly_searches_with_data),
        ("DataFrame 完整", test_results_to_dataframe_full),
        ("DataFrame 無 metrics", test_results_to_dataframe_no_metrics),
    ]
    for name, func in tests:
        try:
            func()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {e}")
            import traceback; traceback.print_exc()
            failed += 1
        print()
    print(f"測試結果: {passed} 通過, {failed} 失敗, 共 {len(tests)} 項")
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
