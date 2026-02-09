from __future__ import annotations

from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


class MissingTokenError(FileNotFoundError):
    """Raised when token.json is missing from the backend folder."""


def _backend_dir() -> Path:
    return Path(__file__).resolve().parent


def load_credentials(token_path: Path | None = None) -> Credentials:
    """
    Load OAuth credentials from token.json (previously created manually).

    This function does NOT run any OAuth flow. It only reads an existing token.
    """
    token_path = token_path or (_backend_dir() / "token.json")

    if not token_path.exists():
        raise MissingTokenError(
            "Missing token.json. Run auth_once.py once to generate it, then try again."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    # If the token is expired but has a refresh token, refresh it silently.
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_path.write_text(creds.to_json(), encoding="utf-8")

    if not creds.valid:
        raise ValueError(
            "token.json is present but credentials are not valid. "
            "Re-run auth_once.py to generate a fresh token.json."
        )

    return creds


def build_gmail_service(creds: Credentials):
    """Create a Gmail API service client."""
    return build("gmail", "v1", credentials=creds)


def fetch_latest_emails(
    max_results: int = 10,
    user_id: str = "me",
    last_days: int | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch Gmail messages from the last `last_days` days.

    Examples:
    - last_days=1 → last 24 hours
    - last_days=7 → last 7 days
    - last_days=None → most recent messages (no date filter)
    """
    creds = load_credentials()
    service = build_gmail_service(creds)

    # ✅ SAFE Gmail search query handling
    query = None
    if last_days is not None:
        query = f"newer_than:{last_days}d"

    resp = service.users().messages().list(
        userId=user_id,
        maxResults=max_results,
        q=query,  # Gmail ignores this if None
    ).execute()

    messages = resp.get("messages", [])
    emails: list[dict[str, Any]] = []

    for msg in messages:
        msg_id = msg.get("id")
        if not msg_id:
            continue

        full = (
            service.users()
            .messages()
            .get(
                userId=user_id,
                id=msg_id,
                format="metadata",
                metadataHeaders=["Subject", "From"],
            )
            .execute()
        )

        headers = full.get("payload", {}).get("headers", [])
        subject = ""
        from_email = ""

        for h in headers:
            name = h.get("name", "").lower()
            if name == "subject":
                subject = h.get("value", "") or ""
            elif name == "from":
                from_email = h.get("value", "") or ""

        emails.append(
            {
                "id": full.get("id"),
                "threadId": full.get("threadId"),
                "subject": subject,
                "snippet": full.get("snippet", ""),
                "from": from_email,
            }
        )

    return emails



