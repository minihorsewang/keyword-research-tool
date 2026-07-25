from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/adwords"]


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    credentials_path = project_root / "credentials.json"

    if not credentials_path.exists():
        raise FileNotFoundError(
            f"找不到 credentials.json：{credentials_path}"
        )

    flow = InstalledAppFlow.from_client_secrets_file(
        str(credentials_path),
        scopes=SCOPES,
    )

    credentials = flow.run_local_server(
        host="localhost",
        port=0,
        access_type="offline",
        prompt="consent",
    )

    if not credentials.refresh_token:
        raise RuntimeError(
            "沒有取得 Refresh Token，請重新執行並確認授權。"
        )

    print("\nRefresh Token：")
    print(credentials.refresh_token)
    print("\n請妥善保存，不要上傳 GitHub。")


if __name__ == "__main__":
    main()
