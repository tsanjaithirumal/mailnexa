from __future__ import annotations

from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main() -> None:
    backend_dir = Path(__file__).resolve().parent
    credentials_path = backend_dir / "credentials.json"
    token_path = backend_dir / "token.json"

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
    creds = flow.run_local_server(port=0)

    token_path.write_text(creds.to_json(), encoding="utf-8")
    print("token.json created successfully")


if __name__ == "__main__":
    main()

