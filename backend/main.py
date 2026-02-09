"""
Mailnexa API (FastAPI).

Architecture note (good for demos/viva):
- The API layer (`main.py`) does not contain Gmail/OAuth logic directly.
- Gmail token creation is a one-time manual step (`auth_once.py`).
- Email fetching (`gmail_reader.py`), classification (`classifier.py`), and orchestration
  (`pipeline.py`) are reusable modules that can be unit-tested independently.
"""

from collections import Counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# Minimal FastAPI app for the Mailnexa backend.
# No Gmail / OAuth logic yet — just basic endpoints + CORS for extension support.

PROJECT_NAME = "Mailnexa"

app = FastAPI(title=PROJECT_NAME)

# Allow requests from any origin (useful for Chrome extensions during development).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict:
    return {"project": PROJECT_NAME, "status": "running"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/emails")
def get_emails(days: int = 1) -> dict:
    """
    Fetch and classify emails from the last N days.
    Default: last 1 day
    """
    try:
        try:
            from .pipeline import run_pipeline
        except ImportError:
            from pipeline import run_pipeline

        emails = run_pipeline(last_days=days)
        return {"emails": emails}

    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch/classify emails: {e}",
        ) from e



@app.get("/emails/summary")
def get_emails_summary() -> dict:
    """
    Fetch and classify the latest emails, then return a simple summary:
    - count per category
    - count per priority
    """
    try:
        try:
            from .pipeline import run_pipeline
        except ImportError:
            from pipeline import run_pipeline

        emails = run_pipeline(last_days=1)

        category_counts = Counter((e.get("category") or "UNKNOWN") for e in emails)
        priority_counts = Counter((e.get("priority") or "UNKNOWN") for e in emails)

        return {
            "total": len(emails),
            "by_category": dict(category_counts),
            "by_priority": dict(priority_counts),
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail="Missing Gmail dependencies. Install Google API client libraries to use /emails/summary.",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to build email summary: {e}",
        ) from e

