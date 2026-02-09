"""
Mailnexa backend package.

Architecture (demo-friendly):
- `auth_once.py`: run manually once to create `token.json`
- `gmail_reader.py`: loads token + fetches email metadata (no OAuth flow)
- `classifier.py`: rule-based classifier (designed to be swapped with ML later)
- `pipeline.py`: orchestration layer (fetch -> classify -> return)
- `main.py`: FastAPI routes (API layer only)
"""

