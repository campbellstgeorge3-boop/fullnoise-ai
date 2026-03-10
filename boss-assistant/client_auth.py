"""
Client portal auth: magic-link tokens and session helpers.
Tokens stored in client_tokens.json (created in project root). Expiry 1 hour.
"""
import json
import secrets
import time
from pathlib import Path

TOKENS_FILE = Path(__file__).resolve().parent / "client_tokens.json"
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour


def _load_tokens() -> dict:
    if not TOKENS_FILE.is_file():
        return {}
    try:
        return json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_tokens(data: dict) -> None:
    TOKENS_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKENS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def create_magic_link_token(client_id: str) -> str:
    """Create a one-time token for the client; store with expiry. Returns the token string."""
    token = secrets.token_urlsafe(32)
    data = _load_tokens()
    data[token] = {
        "client_id": (client_id or "").strip(),
        "expires_at": time.time() + TOKEN_EXPIRY_SECONDS,
    }
    _save_tokens(data)
    return token


def verify_magic_link_token(token: str) -> str | None:
    """
    Verify token; if valid and not expired, return client_id and delete the token.
    Otherwise return None.
    """
    if not token or not token.strip():
        return None
    data = _load_tokens()
    entry = data.get(token.strip())
    if not entry or not isinstance(entry, dict):
        return None
    client_id = (entry.get("client_id") or "").strip()
    expires_at = entry.get("expires_at") or 0
    if not client_id or time.time() > expires_at:
        data.pop(token.strip(), None)
        _save_tokens(data)
        return None
    del data[token.strip()]
    _save_tokens(data)
    return client_id
