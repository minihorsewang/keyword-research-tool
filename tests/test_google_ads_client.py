import sys, os, tempfile
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.google_ads_client import get_client, get_customer_id


def test_get_client_file_not_found():
    try:
        get_client("/nonexistent/google-ads.yaml")
        assert False, "應該拋出 FileNotFoundError"
    except FileNotFoundError:
        print("  PASS: google-ads.yaml 不存在拋錯")


@patch("src.google_ads_client.GoogleAdsClient.load_from_storage")
def test_get_client_success(mock_load):
    mock_load.return_value = MagicMock()
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        f.write(b"dummy")
        tmp = f.name
    try:
        client = get_client(tmp)
        assert client is not None
        mock_load.assert_called_once()
        print("  PASS: get_client 成功")
    finally:
        os.unlink(tmp)


def test_get_customer_id_from_cli():
    client = MagicMock()
    client.config = {"customer_id": "placeholder"}
    result = get_customer_id(client, "1234567890")
    assert result == "1234567890"
    print("  PASS: CLI customer_id 優先")


def test_get_customer_id_from_config():
    client = MagicMock()
    client.config = {"customer_id": "9876543210"}
    result = get_customer_id(client, None)
    assert result == "9876543210"
    print("  PASS: 從 config 讀取 customer_id")


def test_get_customer_id_placeholder():
    client = MagicMock()
    client.config = {"customer_id": "你的正式 Google Ads 帳戶 ID（去掉橫線）"}
    try:
        get_customer_id(client, None)
        assert False, "應該拋出 ValueError"
    except ValueError:
        print("  PASS: placeholder customer_id 拋錯")


def test_get_customer_id_missing():
    client = MagicMock()
    client.config = {}
    try:
        get_customer_id(client, None)
        assert False, "應該拋出 ValueError"
    except ValueError:
        print("  PASS: 缺少 customer_id 拋錯")


def run_all_tests():
    passed = failed = 0
    tests = [
        ("YAML 不存在", test_get_client_file_not_found),
        ("YAML 載入成功", test_get_client_success),
        ("CLI 指定 customer_id", test_get_customer_id_from_cli),
        ("Config 讀取 customer_id", test_get_customer_id_from_config),
        ("Placeholder 拋錯", test_get_customer_id_placeholder),
        ("缺少 customer_id 拋錯", test_get_customer_id_missing),
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
