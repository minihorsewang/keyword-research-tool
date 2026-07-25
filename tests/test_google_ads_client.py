import sys, os, tempfile, logging
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml
from src.google_ads_client import (
    get_client, get_customer_id, validate_customer_id,
    _translate_yaml_error, _load_query_config,
)


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


@patch("src.google_ads_client.GoogleAdsClient.load_from_storage")
def test_get_client_yaml_syntax_error(mock_load):
    mock_load.side_effect = yaml.YAMLError("invalid yaml")
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        f.write(b"dummy")
        tmp = f.name
    try:
        get_client(tmp)
        assert False, "應拋出 ValueError"
    except ValueError as e:
        assert "YAMLError" not in str(e)
        assert "格式錯誤" in str(e)
        print("  PASS: YAML 格式錯誤轉為中文")
    finally:
        os.unlink(tmp)


@patch("src.google_ads_client.GoogleAdsClient.load_from_storage")
def test_get_client_missing_refresh_token(mock_load):
    mock_load.side_effect = ValueError("refresh_token is required")
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        f.write(b"dummy")
        tmp = f.name
    try:
        get_client(tmp)
        assert False, "應拋出 ValueError"
    except ValueError as e:
        assert "refresh_token" in str(e)
        print("  PASS: 缺少 refresh_token 轉為中文")
    finally:
        os.unlink(tmp)


def test_translate_yaml_error_known():
    result = _translate_yaml_error("missing developer_token")
    assert "developer_token" in result
    print("  PASS: 已知欄位名稱翻譯")


def test_translate_yaml_error_unknown():
    result = _translate_yaml_error("some random error")
    assert "設定錯誤" in result
    print("  PASS: 未知錯誤保留原文")


def test_validate_customer_id_ok():
    result = validate_customer_id("1234567890")
    assert result == "1234567890"
    print("  PASS: 有效 customer_id")


def test_validate_customer_id_with_dashes():
    result = validate_customer_id("123-456-7890")
    assert result == "1234567890"
    print("  PASS: 含橫線 customer_id")


def test_validate_customer_id_leading_zeros():
    result = validate_customer_id("0123456789")
    assert result == "0123456789"
    print("  PASS: 保留前導零")


def test_validate_customer_id_too_short():
    try:
        validate_customer_id("12345")
        assert False, "應拋出 ValueError"
    except ValueError as e:
        assert "長度錯誤" in str(e)
        print("  PASS: customer_id 太短拋錯")


def test_validate_customer_id_non_digit():
    try:
        validate_customer_id("12345abcde")
        assert False, "應拋出 ValueError"
    except ValueError as e:
        assert "格式錯誤" in str(e)
        print("  PASS: customer_id 含非數字拋錯")


def test_get_customer_id_from_cli():
    client = MagicMock()
    result = get_customer_id(client, "1234567890")
    assert result == "1234567890"
    print("  PASS: CLI customer_id 優先")


def test_get_customer_id_from_cli_leading_zero():
    client = MagicMock()
    result = get_customer_id(client, "0123456789")
    assert result == "0123456789"
    print("  PASS: CLI 前導零保留")


@patch("src.google_ads_client._load_query_config")
def test_get_customer_id_from_query_config(mock_load):
    mock_load.return_value = {"customer_id": "9876543210"}
    client = MagicMock()
    result = get_customer_id(client, None)
    assert result == "9876543210"
    print("  PASS: 從 google_query.json 讀取 customer_id")


@patch("src.google_ads_client._load_query_config")
def test_get_customer_id_missing_no_config(mock_load):
    mock_load.return_value = {"customer_id": ""}
    client = MagicMock()
    try:
        get_customer_id(client, None)
        assert False, "應該拋出 ValueError"
    except ValueError as e:
        assert "config/google_query.json" in str(e)
        print("  PASS: 缺少 customer_id 拋錯（含正確提示）")


def _capture_log(name, level, func):
    import io
    saved_disable = logging.root.manager.disable
    logging.disable(logging.NOTSET)
    logger = logging.getLogger(name)
    old_level = logger.level
    logger.setLevel(level)
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    logger.addHandler(handler)
    try:
        func()
        return stream.getvalue()
    finally:
        logger.removeHandler(handler)
        logger.setLevel(old_level)
        logging.disable(saved_disable)


def test_get_customer_id_mcc_warning():
    def check():
        client = MagicMock()
        client.config = {"login_customer_id": "1234567890"}
        with patch("src.google_ads_client._load_query_config", return_value={"customer_id": "1234567890"}):
            result = get_customer_id(client, None)
        assert result == "1234567890"
    output = _capture_log("src.google_ads_client", logging.WARNING, check)
    assert "MCC" in output
    print("  PASS: MCC 與 customer_id 相同時發出警告")


def test_get_customer_id_mcc_different():
    def check():
        client = MagicMock()
        client.config = {"login_customer_id": "2222222222"}
        with patch("src.google_ads_client._load_query_config", return_value={"customer_id": "1111111111"}):
            result = get_customer_id(client, None)
        assert result == "1111111111"
    output = _capture_log("src.google_ads_client", logging.INFO, check)
    assert "MCC" in output and "2222222222" in output
    print("  PASS: MCC 與 customer_id 不同時正常記錄")


def run_all_tests():
    passed = failed = 0
    tests = [
        ("YAML 不存在", test_get_client_file_not_found),
        ("YAML 載入成功", test_get_client_success),
        ("YAML 格式錯誤", test_get_client_yaml_syntax_error),
        ("缺少 refresh_token", test_get_client_missing_refresh_token),
        ("翻譯已知欄位", test_translate_yaml_error_known),
        ("翻譯未知錯誤", test_translate_yaml_error_unknown),
        ("有效 customer_id", test_validate_customer_id_ok),
        ("含橫線 customer_id", test_validate_customer_id_with_dashes),
        ("保留前導零", test_validate_customer_id_leading_zeros),
        ("customer_id 太短", test_validate_customer_id_too_short),
        ("customer_id 含非數字", test_validate_customer_id_non_digit),
        ("CLI 指定 customer_id", test_get_customer_id_from_cli),
        ("CLI 前導零保留", test_get_customer_id_from_cli_leading_zero),
        ("Query config 讀取 customer_id", test_get_customer_id_from_query_config),
        ("缺少 customer_id 拋錯", test_get_customer_id_missing_no_config),
        ("MCC 警告", test_get_customer_id_mcc_warning),
        ("MCC 不同", test_get_customer_id_mcc_different),
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
