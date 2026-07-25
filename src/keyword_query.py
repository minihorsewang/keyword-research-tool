import logging

from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)

LANGUAGE_CHINESE = "languageConstants/1005"
GEO_TAIWAN = "geoTargetConstants/2392"
NETWORK_GOOGLE_SEARCH = 2


def query_keyword_ideas(client, customer_id, seed_keywords):
    keyword_plan_idea_service = client.get_service("KeywordPlanIdeaService")

    request = client.get_type("GenerateKeywordIdeasRequest")
    request.customer_id = customer_id
    request.language = LANGUAGE_CHINESE
    request.geo_target_constants.append(GEO_TAIWAN)
    request.keyword_plan_network = NETWORK_GOOGLE_SEARCH
    request.keyword_seed.keywords.extend(seed_keywords)

    logger.info(f"查詢關鍵字: {seed_keywords}")
    response = keyword_plan_idea_service.generate_keyword_ideas(
        request=request
    )
    results = list(response)
    logger.info(f"取得 {len(results)} 個建議關鍵字")
    return results


def query_with_retry(client, customer_id, seed_keywords, max_retries=3):
    for attempt in range(max_retries):
        try:
            return query_keyword_ideas(client, customer_id, seed_keywords)
        except GoogleAdsException as e:
            logger.warning(f"API 查詢失敗 (第 {attempt+1} 次): {e}")
            if attempt == max_retries - 1:
                raise
    return []
