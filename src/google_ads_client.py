import logging
from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

logger = logging.getLogger(__name__)


def get_client(config_path=None):
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"找不到 google-ads.yaml：{config_path}")
    client = GoogleAdsClient.load_from_storage(str(config_path))
    logger.info("GoogleAdsClient 初始化完成")
    return client


def get_customer_id(client):
    raw = client.config.get("login_customer_id", "")
    return raw.lstrip("0") or "0"
