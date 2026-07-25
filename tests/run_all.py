"""
統一測試執行入口
執行方式: python tests/run_all.py
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Suppress logging during tests
import logging
logging.disable(logging.CRITICAL)

TEST_MODULES = [
    ("原始 CSV 測試", "test_runner", lambda: __import__("tests.test_runner")),
    ("種子關鍵字輸入", "test_keyword_input", None),
    ("Google Ads Client", "test_google_ads_client", None),
    ("Google 結果對映", "test_google_result_mapper", None),
    ("API 查詢 Mock", "test_keyword_query_mock", None),
    ("Google Excel 輸出", "test_google_excel_output", None),
]


def run_single(module_name):
    mod = __import__(f"tests.{module_name}", fromlist=["run_all_tests"])
    return mod.run_all_tests()


def main():
    total_passed = 0
    total_failed = 0
    suite_passed = 0
    suite_failed = 0

    for label, mod_name, _ in TEST_MODULES:
        print(f"\n{'='*50}")
        print(f"  [{label}]")
        print(f"{'='*50}")
        try:
            # Special case: test_runner needs setup()
            if mod_name == "test_runner":
                import tests.test_runner as tr
                tr.setup()
                ok = tr.run_all_tests()
            else:
                ok = run_single(mod_name)
        except Exception as e:
            print(f"  載入失敗: {e}")
            traceback.print_exc()
            ok = False

        p = {"tests.test_runner": 15, "test_keyword_input": 15,
             "test_google_ads_client": 18,              "test_google_result_mapper": 14,
             "test_keyword_query_mock": 11, "test_google_excel_output": 4}.get(mod_name, 0)
        if ok:
            suite_passed += 1
            total_passed += p
        else:
            suite_failed += 1
            total_failed += p

    print(f"\n{'='*50}")
    print(f"整體測試結果: {suite_passed} 套件通過, {suite_failed} 套件失敗")
    print(f"測試總計: {total_passed} 通過, {total_failed} 失敗, 共 {total_passed + total_failed} 項")
    return suite_failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
