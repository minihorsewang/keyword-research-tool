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


def get_customer_id(client, cli_customer_id=None):
    if cli_customer_id:
        return cli_customer_id
    raw = client.config.get("customer_id", "")
    if raw and raw != "你的正式 Google Ads 帳戶 ID（去掉橫線）":
        return raw
    raise ValueError(
        "缺少 customer_id。請在 google-ads.yaml 設定正式查詢帳戶 ID，\n"
        "或使用 --customer-id 1234567890 指定。"
    )
