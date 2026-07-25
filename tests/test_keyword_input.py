import sys, os, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.keyword_input import (
    load_keywords_from_file, load_keywords_from_cli,
    clean_and_deduplicate, resolve_seed_keywords,
)


def test_load_keywords_from_file_exists():
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write("貼紙印刷\n標籤印刷\n")
        tmp = f.name
    try:
        result = load_keywords_from_file(tmp)
        assert result == ["貼紙印刷", "標籤印刷"]
        print("  PASS: 從檔案載入關鍵字")
    finally:
        os.unlink(tmp)


def test_load_keywords_from_file_not_found():
    try:
        load_keywords_from_file("/nonexistent/file.txt")
        assert False, "應該拋出 FileNotFoundError"
    except FileNotFoundError:
        print("  PASS: 找不到檔案正確拋錯")


def test_load_keywords_from_file_skips_empty():
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False, suffix=".txt") as f:
        f.write("貼紙印刷\n\n\n標籤印刷\n")
        tmp = f.name
    try:
        result = load_keywords_from_file(tmp)
        assert result == ["貼紙印刷", "標籤印刷"]
        print("  PASS: 跳過空白行")
    finally:
        os.unlink(tmp)


def test_load_keywords_from_cli():
    result = load_keywords_from_cli("貼紙印刷,標籤印刷, 名片印刷 ")
    assert result == ["貼紙印刷", "標籤印刷", "名片印刷"]
    print("  PASS: CLI 關鍵字解析")


def test_load_keywords_from_cli_empty():
    result = load_keywords_from_cli("")
    assert result == []
    print("  PASS: 空 CLI 字串回傳空串列")


def test_clean_and_deduplicate():
    raw = ["貼紙印刷", " 貼紙印刷 ", "貼紙印刷", "標籤印刷"]
    result = clean_and_deduplicate(raw)
    assert result == ["貼紙印刷", "標籤印刷"]
    print("  PASS: 去重與清理")


def test_clean_and_deduplicate_all_empty():
    result = clean_and_deduplicate(["", "  ", "　"])
    assert result == []
    print("  PASS: 全空白自動過濾")


def test_resolve_seed_keywords_with_cli():
    result = resolve_seed_keywords("貼紙印刷,標籤印刷")
    assert "貼紙印刷" in result
    assert "標籤印刷" in result
    print("  PASS: resolve_seed_keywords 使用 CLI 參數")


def run_all_tests():
    passed = failed = 0
    tests = [
        ("從檔案載入關鍵字", test_load_keywords_from_file_exists),
        ("找不到檔案拋錯", test_load_keywords_from_file_not_found),
        ("跳過空白行", test_load_keywords_from_file_skips_empty),
        ("CLI 關鍵字解析", test_load_keywords_from_cli),
        ("空 CLI 字串", test_load_keywords_from_cli_empty),
        ("去重與清理", test_clean_and_deduplicate),
        ("全空白自動過濾", test_clean_and_deduplicate_all_empty),
        ("resolve seed keywords", test_resolve_seed_keywords_with_cli),
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
