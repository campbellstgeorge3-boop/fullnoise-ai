"""
Load and look up clients from clients.json.
Used by the reply-by-email flow to find which client sent a message.
"""
import json
import re
from pathlib import Path
from typing import Any


def _clients_path() -> Path:
    return Path(__file__).resolve().parent / "clients.json"


def _normalize_email(addr: str) -> str:
    """Extract a clean email from 'Name <email@domain.com>' or return lowercased addr."""
    if not addr or not isinstance(addr, str):
        return ""
    addr = addr.strip()
    match = re.search(r"<([^>]+)>", addr)
    if match:
        return match.group(1).strip().lower()
    return addr.lower()


def load_clients() -> list[dict[str, Any]]:
    """Load clients from clients.json. Returns list of client dicts."""
    path = _clients_path()
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("clients") or []
    except (json.JSONDecodeError, OSError):
        return []


def get_client(clients: list[dict[str, Any]], client_id: str) -> dict[str, Any] | None:
    """Return the client dict with the given id, or None."""
    if not client_id or not clients:
        return None
    want = (client_id or "").strip()
    for c in clients:
        if (c.get("id") or "").strip() == want:
            return c
    return None


def get_client_by_email(clients: list[dict[str, Any]], from_address: str) -> dict[str, Any] | None:
    """
    Find a client whose email_to matches the given from_address.
    from_address can be 'Name <email@domain.com>' or 'email@domain.com'.
    """
    if not from_address or not clients:
        return None
    want = _normalize_email(from_address)
    if not want:
        return None
    for c in clients:
        to_email = (c.get("email_to") or "").strip()
        if _normalize_email(to_email) == want:
            return c
    return None
