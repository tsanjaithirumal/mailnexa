from __future__ import annotations

from typing import Any

# Pipeline layer: orchestrates "fetch -> classify"
try:
    from .classifier import (
        EmailClassifier,
        classify_emails,
        HybridEmailClassifier,
    )
except ImportError:
    from classifier import (
        EmailClassifier,
        classify_emails,
        HybridEmailClassifier,
    )


def run_pipeline(
    max_results: int = 50,
    user_id: str = "me",
    last_days: int | None = 1,   # ✅ default = last 24 hours
) -> list[dict[str, Any]]:
    """
    End-to-end processing pipeline:
    1) Fetch Gmail emails (last N days)
    2) Classify using Hybrid classifier (Rules + ML)
    3) Return enriched emails
    """
    try:
        from .gmail_reader import fetch_latest_emails
    except ImportError:
        from gmail_reader import fetch_latest_emails

    # 1️⃣ Fetch emails
    emails = fetch_latest_emails(
        max_results=max_results,
        user_id=user_id,
        last_days=last_days,
    )

    # 2️⃣ Use Hybrid classifier (IMPORTANT)
    classifier = HybridEmailClassifier()

    # 3️⃣ Classify and return
    return classify_emails(emails, classifier=classifier)


def process_emails(
    emails: list[dict[str, Any]],
    classifier: EmailClassifier | None = None,
) -> list[dict[str, Any]]:
    """
    Classify already-fetched emails.
    """
    classifier = classifier or HybridEmailClassifier()
    return classify_emails(emails, classifier=classifier)
