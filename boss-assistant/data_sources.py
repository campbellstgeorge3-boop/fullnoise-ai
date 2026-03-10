"""
Pluggable data sources for Boss Assistant.
Each source returns (BossInput, report_month, recipient_first_name).
"""
import os
from pathlib import Path
from typing import Optional

from utils import BossInput, validate_and_parse

ROOT = Path(__file__).resolve().parent
DEFAULT_PDFS_DIR = ROOT / "vision_data" / "pdfs_downloaded"
DEFAULT_CSV_PATH = ROOT / "vision_data" / "vision_12months_from_drive.csv"


def load_from_google_drive(
    folder_id: Optional[str] = None,
    pdfs_dir: Optional[Path] = None,
    csv_path: Optional[Path] = None,
) -> tuple[BossInput, Optional[str], Optional[str]]:
    """
    Sync PDFs from Drive, extract to CSV, load BossInput.
    Returns (inp, report_month, recipient_first_name).
    """
    from drive_oauth import sync_pdfs_from_drive, DEFAULT_FOLDER_ID
    from pdf_to_csv import build_csv_from_pdf_dir
    from data_loader import load_from_12month_csv

    folder_id = folder_id or os.environ.get("GOOGLE_DRIVE_FOLDER_ID") or DEFAULT_FOLDER_ID
    pdfs_dir = pdfs_dir or DEFAULT_PDFS_DIR
    csv_path = csv_path or DEFAULT_CSV_PATH

    sync_pdfs_from_drive(folder_id, pdfs_dir)
    report_path = csv_path.parent / "extraction_report.json"
    build_csv_from_pdf_dir(pdfs_dir, csv_path, out_report_json=report_path)

    inp_12 = load_from_12month_csv(csv_path)
    inp = validate_and_parse(
        revenue_this_month=inp_12.revenue_this_month,
        revenue_last_month=inp_12.revenue_last_month,
        budget_this_month=inp_12.budget_this_month,
        costs_this_month=getattr(inp_12, "costs_this_month", 0.0),
        jobs_this_month=inp_12.jobs_this_month,
        jobs_last_month=inp_12.jobs_last_month,
    )

    report_month = _report_month_from_csv(csv_path)
    recipient = (os.environ.get("REPORT_RECIPIENT_FIRST_NAME") or "").strip() or None
    return inp, report_month, recipient


def load_from_myob_source(config: Optional[dict] = None) -> tuple[BossInput, Optional[str], Optional[str]]:
    """
    Pull data from MYOB P&L API; build BossInput.
    Returns (inp, report_month, recipient_first_name).
    Config from env or passed dict.
    """
    from datetime import datetime
    from myob_loader import load_from_myob_config

    config = config or {}
    for key in ("myob_cf_uri", "myob_budget", "myob_jobs_this", "myob_jobs_last"):
        if key not in config and os.environ.get(key.upper().replace("MYOB_", "MYOB_")):
            config[key] = os.environ.get(key.upper().replace("MYOB_", "MYOB_"))
    if "myob_cf_uri" not in config:
        config["myob_cf_uri"] = os.environ.get("MYOB_CF_URI")

    inp_myob = load_from_myob_config(config)
    inp = validate_and_parse(
        revenue_this_month=inp_myob.revenue_this_month,
        revenue_last_month=inp_myob.revenue_last_month,
        budget_this_month=inp_myob.budget_this_month,
        costs_this_month=getattr(inp_myob, "costs_this_month", 0.0),
        jobs_this_month=inp_myob.jobs_this_month,
        jobs_last_month=inp_myob.jobs_last_month,
    )
    report_month = datetime.now().strftime("%Y-%m")
    recipient = (os.environ.get("REPORT_RECIPIENT_FIRST_NAME") or "").strip() or None
    return inp, report_month, recipient


def _report_month_from_csv(path: Path) -> Optional[str]:
    """Extract YYYY-MM from last row of CSV."""
    import csv
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
        if len(rows) < 2:
            return None
        headers = [h.strip().lower() for h in rows[0]]
        mi = next((i for i, h in enumerate(headers) if h in ("month", "month_name")), None)
        if mi is None:
            return None
        data_rows = [r for r in rows[1:] if r and len(r) > mi and (r[mi] or "").strip()]
        if not data_rows:
            return None
        m = (data_rows[-1][mi] or "").strip()
        if len(m) >= 7 and m[4] == "-":
            return m[:7]
    except Exception:
        pass
    return None


def load_input(
    source: str = "google_drive",
    *,
    folder_id: Optional[str] = None,
    pdfs_dir: Optional[Path] = None,
    csv_path: Optional[Path] = None,
    myob_config: Optional[dict] = None,
) -> tuple[BossInput, Optional[str], Optional[str]]:
    """
    Load BossInput from the specified data source.
    source: "google_drive" | "myob"
    Returns (inp, report_month, recipient_first_name).
    """
    src = (source or "").strip().lower().replace("-", "_")
    if src == "google_drive":
        return load_from_google_drive(folder_id=folder_id, pdfs_dir=pdfs_dir, csv_path=csv_path)
    if src == "myob":
        return load_from_myob_source(config=myob_config)
    raise ValueError(
        f"Unknown data source: {source}. Use google_drive or myob."
    )
