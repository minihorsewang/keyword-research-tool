import json
import logging
from pathlib import Path

from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)

NETWORK_MAP = {
    "GOOGLE_SEARCH": 2,
    "GOOGLE_SEARCH_AND_PARTNERS": 3,
}


def load_query_config():
    path = Path(__file__).resolve().parent.parent / "config" / "google_query.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


CONFIG = load_query_config()


RETRIABLE_ERRORS = {"RATE_LIMIT_EXCEEDED",}


def format_google_ads_error(error):
    parts = [f"Request ID：{error.request_id}"]
    for api_error in error.failure.errors:
        code = api_error.error_code
        msg = api_error.message

        if code.authentication_error:
            parts.append(f"認證錯誤：{code.authentication_error.name}")
        elif code.authorization_error:
            auth_code = code.authorization_error.name
            if auth_code == "DEVELOPER_TOKEN_NOT_APPROVED":
                parts.append(
                    "Developer Token 尚未取得 Basic Access。\n"
                    "無法查詢正式 Google Ads 帳戶。"
                )
            elif auth_code in ("DEVELOPER_TOKEN_NOT_ALLOWED", "CUSTOMER_NOT_FOUND"):
                parts.append(f"授權錯誤：{auth_code} — 請確認 Customer ID 是否正確且有權限存取。")
            else:
                parts.append(f"授權錯誤：{auth_code}")
        elif code.rate_limit_error:
            parts.append(f"配額限制：{code.rate_limit_error.name}")
        elif code.keyword_plan_idea_error:
            parts.append(f"關鍵字查詢錯誤：{code.keyword_plan_idea_error.name}")
        else:
            parts.append(f"錯誤代碼：{code.WhichOneof('error_code') or 'unknown'}")

        if msg:
            parts.append(f"說明：{msg}")

    return "\n".join(parts)


def is_retriable(error):
    for api_error in error.failure.errors:
        code = api_error.error_code
        if code.rate_limit_error and code.rate_limit_error.name in RETRIABLE_ERRORS:
            return True
    return False


def query_keyword_ideas(client, customer_id, seed_keywords, config=None):
    if config is None:
        config = CONFIG
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = config["language"]
    request.geo_target_constants.append(config["geo_target"])
    request.keyword_plan_network = NETWORK_MAP.get(config["keyword_plan_network"], 2)
    request.keyword_seed.keywords.extend(seed_keywords)

    logger.info(f"查詢關鍵字: {seed_keywords}")
    logger.info(f"查詢條件: 語言={config['language_name']}, 地區={config['geo_target_name']}, "
                f"網路={config['keyword_plan_network']}")
    response = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )
    results = list(response)
    logger.info(f"取得 {len(results)} 個建議關鍵字")
    return results


def query_with_retry(client, customer_id, seed_keywords, max_retries=None):
    if max_retries is None:
        max_retries = CONFIG.get("max_retries", 3)
    last_error = None
    for attempt in range(max_retries):
        try:
            return query_keyword_ideas(client, customer_id, seed_keywords)
        except GoogleAdsException as e:
            last_error = e
            detail = format_google_ads_error(e)
            logger.warning(f"API 查詢失敗 (第 {attempt+1}/{max_retries} 次):\n{detail}")
            if not is_retriable(e):
                logger.error("非可重試錯誤，停止重試")
                raise
    raise last_error
