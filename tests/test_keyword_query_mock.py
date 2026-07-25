import sys, os
from unittest.mock import MagicMock, patch, call
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.keyword_query import (
    load_query_config, format_google_ads_error, is_retriable,
    query_keyword_ideas, query_with_retry,
)


def test_load_query_config():
    config = load_query_config()
    assert "language" in config
    assert "geo_target" in config
    assert "keyword_plan_network" in config
    assert config["language_name"] == "中文 (繁體)"
    print("  PASS: 載入查詢設定")


from google.ads.googleads.errors import GoogleAdsException


class FakeErrorCode:
    def __init__(self):
        self.authentication_error = None
        self.authorization_error = None
        self.rate_limit_error = None
        self.keyword_plan_idea_error = None

    def WhichOneof(self, _):
        return "unknown"


class FakeApiError:
    def __init__(self, code, message=""):
        self.error_code = code
        self.message = message


class FakeEnumVal:
    def __init__(self, name):
        self.name = name


def make_code(err_type, val):
    c = FakeErrorCode()
    if err_type == "auth":
        c.authentication_error = FakeEnumVal(val)
    elif err_type == "authorization":
        c.authorization_error = FakeEnumVal(val)
    elif err_type == "rate_limit":
        c.rate_limit_error = FakeEnumVal(val)
    elif err_type == "keyword_plan":
        c.keyword_plan_idea_error = FakeEnumVal(val)
    return c


def make_error(err_type, val, msg=""):
    class FakeFailure:
        errors = [FakeApiError(make_code(err_type, val), msg)]
    error = GoogleAdsException.__new__(GoogleAdsException)
    error.request_id = "REQ-001"
    error.failure = FakeFailure()
    return error


def test_format_auth_error():
    error = make_error("auth", "INVALID_CREDENTIALS", "credential fail")
    result = format_google_ads_error(error)
    assert "Request ID：REQ-001" in result
    assert "認證錯誤" in result
    print("  PASS: 認證錯誤格式化")


def test_format_developer_token_error():
    error = make_error("authorization", "DEVELOPER_TOKEN_NOT_APPROVED")
    result = format_google_ads_error(error)
    assert "Basic Access" in result
    assert "REQ-001" in result
    print("  PASS: Developer Token 錯誤訊息")


def test_format_authorization_error():
    error = make_error("authorization", "CUSTOMER_NOT_FOUND")
    result = format_google_ads_error(error)
    assert "授權錯誤" in result
    print("  PASS: 授權錯誤格式化")


def test_format_rate_limit_error():
    error = make_error("rate_limit", "RATE_LIMIT_EXCEEDED")
    result = format_google_ads_error(error)
    assert "配額限制" in result
    print("  PASS: 配額限制錯誤")


def test_is_retriable_true():
    error = make_error("rate_limit", "RATE_LIMIT_EXCEEDED")
    assert is_retriable(error) is True
    print("  PASS: 可重試錯誤")


def test_is_retriable_false():
    error = make_error("auth", "INVALID_CREDENTIALS")
    assert is_retriable(error) is False
    print("  PASS: 不可重試錯誤")


@patch("src.keyword_query.query_keyword_ideas")
def test_query_with_retry_success_first(mock_query):
    mock_query.return_value = ["result1"]
    client = MagicMock()
    result = query_with_retry(client, "123", ["貼紙"], max_retries=3)
    assert result == ["result1"]
    mock_query.assert_called_once()
    print("  PASS: 第一次查詢成功")


@patch("src.keyword_query.query_keyword_ideas")
def test_query_with_retry_retry_then_success(mock_query):
    rate_error = make_error("rate_limit", "RATE_LIMIT_EXCEEDED")
    mock_query.side_effect = [rate_error, rate_error, ["result_ok"]]
    client = MagicMock()
    result = query_with_retry(client, "123", ["貼紙"], max_retries=3)
    assert result == ["result_ok"]
    assert mock_query.call_count == 3
    print("  PASS: 重試兩次後成功")


@patch("src.keyword_query.query_keyword_ideas")
def test_query_with_retry_non_retriable_raises(mock_query):
    auth_error = make_error("auth", "INVALID_CREDENTIALS")
    mock_query.side_effect = auth_error
    client = MagicMock()
    try:
        query_with_retry(client, "123", ["貼紙"], max_retries=3)
        assert False, "應該拋出例外"
    except type(auth_error):
        mock_query.assert_called_once()
        print("  PASS: 非可重試錯誤直接拋出")


@patch("src.keyword_query.query_keyword_ideas")
def test_query_with_retry_all_retries_exhausted(mock_query):
    rate_error = make_error("rate_limit", "RATE_LIMIT_EXCEEDED")
    mock_query.side_effect = [rate_error] * 3
    client = MagicMock()
    try:
        query_with_retry(client, "123", ["貼紙"], max_retries=3)
        assert False, "應該在重試用盡後拋出"
    except type(rate_error):
        assert mock_query.call_count == 3
        print("  PASS: 重試用盡後拋出")


def run_all_tests():
    passed = failed = 0
    tests = [
        ("載入查詢設定", test_load_query_config),
        ("認證錯誤格式化", test_format_auth_error),
        ("Developer Token 錯誤", test_format_developer_token_error),
        ("授權錯誤格式化", test_format_authorization_error),
        ("配額限制錯誤", test_format_rate_limit_error),
        ("可重試判斷", test_is_retriable_true),
        ("不可重試判斷", test_is_retriable_false),
        ("第一次查詢成功", test_query_with_retry_success_first),
        ("重試後成功", test_query_with_retry_retry_then_success),
        ("非可重試直接拋出", test_query_with_retry_non_retriable_raises),
        ("重試用盡拋出", test_query_with_retry_all_retries_exhausted),
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
