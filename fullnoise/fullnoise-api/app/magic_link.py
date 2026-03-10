"""Magic link: create and verify one-time tokens for client login."""
import secrets
import time
from pathlib import Path

# In-memory store for MVP. Replace with Redis or DB for production.
_tokens: dict[str, dict] = {}
TOKEN_TTL = 3600  # 1 hour


def create_token(client_id: str, email: str) -> str:
    token = secrets.token_urlsafe(32)
    _tokens[token] = {"client_id": client_id, "email": email, "exp": time.time() + TOKEN_TTL}
    return token


def verify_token(token: str) -> dict | None:
    if not token or token not in _tokens:
        return None
    data = _tokens.pop(token)
    if time.time() > data["exp"]:
        return None
    return data
