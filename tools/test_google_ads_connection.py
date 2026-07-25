from pathlib import Path

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    config_path = project_root / "google-ads.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"找不到設定檔：{config_path}")

    client = GoogleAdsClient.load_from_storage(str(config_path))

    customer_service = client.get_service("CustomerService")

    try:
        accessible_customers = customer_service.list_accessible_customers()

        print("連線成功，可以存取的 Google Ads 帳戶：")

        if not accessible_customers.resource_names:
            print("目前沒有可存取帳戶。")

        for resource_name in accessible_customers.resource_names:
            print(resource_name)

    except GoogleAdsException as error:
        print("Google Ads API 連線失敗。")
        print(f"Request ID：{error.request_id}")

        for api_error in error.failure.errors:
            print(f"錯誤：{api_error.message}")


if __name__ == "__main__":
    main()
