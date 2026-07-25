import json
import logging
from pathlib import Path

import yaml
from google.ads.googleads.client import GoogleAdsClient

logger = logging.getLogger(__name__)


_YAML_REQUIRED_KEYS = {
    "developer_token": "developer_token",
    "client_id": "client_id",
    "client_secret": "client_secret",
    "refresh_token": "refresh_token",
}


def _translate_yaml_error(msg):
    msg_lower = msg.lower()
    for key, label in _YAML_REQUIRED_KEYS.items():
        if key in msg_lower:
            if key == "refresh_token":
                return (
                    f"google-ads.yaml 缺少 {label}。\n"
                    "請執行 python tools/generate_refresh_token.py 取得"
                )
            return f"google-ads.yaml 缺少 {label}"
    return f"google-ads.yaml 設定錯誤：{msg}"


def _load_query_config():
    path = Path(__file__).resolve().parent.parent / "config" / "google_query.json"
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_client(config_path=None):
    if config_path is None:
        config_path = Path(__file__).resolve().parent.parent / "google-ads.yaml"
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"找不到 google-ads.yaml：{config_path}")
    try:
        client = GoogleAdsClient.load_from_storage(str(config_path))
    except yaml.YAMLError as e:
        raise ValueError(
            "google-ads.yaml 格式錯誤，請檢查：\n"
            f"  1. 縮排是否一致（使用空格）\n"
            f"  2. 冒號後是否有一個空格\n"
            f"  3. 字串值是否正確加引號\n"
            f"詳細錯誤：{e}"
        )
    except ValueError as e:
        raise ValueError(_translate_yaml_error(str(e)))
    logger.info("GoogleAdsClient 初始化完成")
    return client


def validate_customer_id(cid, label="Customer ID"):
    cleaned = cid.replace("-", "").strip()
    if not cleaned.isdigit():
        raise ValueError(f"{label} 格式錯誤：「{cid}」應為 10 位數字（可含前導零）")
    if len(cleaned) != 10:
        raise ValueError(
            f"{label} 長度錯誤：{len(cleaned)} 位，應為 10 位數字\n"
            f"（目前值：「{cid}」，請確認是否去掉橫線且補滿 10 位）"
        )
    return cleaned


def get_customer_id(client, cli_customer_id=None):
    if cli_customer_id:
        validate_customer_id(cli_customer_id, "--customer-id")
        return cli_customer_id
    qconfig = _load_query_config()
    raw = qconfig.get("customer_id", "")
    if not raw:
        raise ValueError(
            "缺少 customer_id。請選擇一種方式：\n"
            "  1. 在 config/google_query.json 設定 customer_id\n"
            '  2. 使用 --customer-id 1234567890 指定\n'
            "（注意：customer_id 不要寫在 google-ads.yaml，該檔案不支援此欄位）"
        )
    validate_customer_id(raw, "customer_id")

    mcc = client.config.get("login_customer_id", "")
    if mcc:
        mcc_clean = mcc.replace("-", "").strip()
        cust_clean = raw.replace("-", "").strip()
        if mcc_clean and mcc_clean == cust_clean:
            logger.warning(
                "login_customer_id（MCC）與 customer_id 相同（均為 %s），\n"
                "請確認這是受管帳戶而非 MCC 帳戶本身。", cust_clean
            )
        else:
            logger.info("MCC 帳戶：%s → 查詢帳戶：%s", mcc_clean, cust_clean)

    return raw
