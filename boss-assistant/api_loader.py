"""
Load Boss Assistant input from an API (URL that returns JSON).
Use for "best" setup: agent pulls data automatically; client doesn't put files in.
"""
import json
import os
import urllib.request
from typing import Optional

from input_model import BossInput, ValidationError


def load_from_api(
    url: str,
    headers: Optional[dict] = None,
    api_key_env: Optional[str] = None,
    company_name: Optional[str] = None,
) -> BossInput:
    """
    GET url; response must be JSON with keys revenue_this_month, revenue_last_month,
    budget_this_month, jobs_this_month, jobs_last_month (and optional company_name, etc.).
    If api_key_env is set, add Authorization: Bearer <value from env> to the request.
    """
    req_headers = dict(headers or {})
    if api_key_env:
        key = os.environ.get(api_key_env)
        if key:
            req_headers["Authorization"] = f"Bearer {key.strip()}"
    req = urllib.request.Request(url, headers=req_headers or None)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("API response must be a JSON object")
    if company_name:
        data["company_name"] = company_name
    return BossInput.from_dict(data)
