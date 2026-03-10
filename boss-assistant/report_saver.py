"""
Auto-save generated reports to reports/<YYYY-MM>_<mode>.txt or .json.
Creates reports/ if missing. If month is unknown, uses timestamp prefix.
Also supports saving "latest" per client for the client portal.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Union

REPORTS_DIR = Path(__file__).resolve().parent / "reports"


def save_latest_for_client(client_id: str, content: Union[str, dict]) -> Path:
    """Save report as the latest for this client (for client portal)."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_id = (client_id or "default").strip().replace("/", "_").replace("..", "") or "default"
    path = REPORTS_DIR / f"latest_{safe_id}.txt"
    if isinstance(content, dict):
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    return path


def get_latest_report(client_id: str) -> str | None:
    """Read the latest saved report for this client, or None if missing."""
    safe_id = (client_id or "default").strip().replace("/", "_").replace("..", "") or "default"
    path = REPORTS_DIR / f"latest_{safe_id}.txt"
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def save_report(
    content: Union[str, dict],
    mode: str,
    report_month: str | None = None,
) -> Path:
    """
    Save report content to reports/<prefix>_<mode>.(txt|json).
    mode: e.g. "text", "json", "live", "dry_run". If mode is "json" or content is dict, writes .json.
    report_month: optional "YYYY-MM". If None, uses timestamp (YYYY-MM-DD_HH-MM).
    Returns the path written.
    """
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    if report_month is not None and report_month.strip():
        prefix = report_month.strip()
    else:
        prefix = datetime.now().strftime("%Y-%m-%d_%H-%M")
    is_json = mode == "json" or isinstance(content, dict)
    ext = ".json" if is_json else ".txt"
    path = REPORTS_DIR / f"{prefix}_{mode}{ext}"
    if isinstance(content, dict):
        path.write_text(json.dumps(content, indent=2, ensure_ascii=False), encoding="utf-8")
    else:
        path.write_text(content, encoding="utf-8")
    return path
