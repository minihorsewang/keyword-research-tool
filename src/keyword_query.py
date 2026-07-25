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
    for attempt in range(max_retries):
        try:
            return query_keyword_ideas(client, customer_id, seed_keywords)
        except GoogleAdsException as e:
            logger.warning(f"API 查詢失敗 (第 {attempt+1} 次): {e}")
            if attempt == max_retries - 1:
                raise
    return []
