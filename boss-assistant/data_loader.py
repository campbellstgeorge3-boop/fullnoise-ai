"""
Load Boss Assistant input from files: JSON or CSV.
Supports a single data file or an inbox folder (use newest file).
"""
import csv
import json
from pathlib import Path
from typing import Optional

from input_model import BossInput, ValidationError

# CSV: required columns (in order if no header)
REQUIRED_KEYS = [
    "revenue_this_month",
    "revenue_last_month",
    "budget_this_month",
    "jobs_this_month",
    "jobs_last_month",
]
OPTIONAL_KEYS = [
    "costs_this_month",
    "company_name",
    "outstanding_quotes_count",
    "overdue_invoices_count",
    "notes",
]


def _normalize_header(s: str) -> str:
    return s.strip().lower().replace(" ", "_").replace("-", "_")


def load_from_json(path: Path) -> BossInput:
    """Load and validate from a JSON file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BossInput.from_dict(raw)


def _parse_value(s: str, key: str):
    s = (s or "").strip()
    if key == "notes" or key == "company_name":
        return s or None
    if key in ("outstanding_quotes_count", "overdue_invoices_count"):
        if not s or s.lower() in ("n", "na", "null", ""):
            return None
        try:
            return int(float(s))
        except (ValueError, TypeError):
            return None
    try:
        if key in ("jobs_this_month", "jobs_last_month"):
            return int(float(s)) if s else 0
        return float(s) if s else 0.0
    except (ValueError, TypeError):
        return 0.0 if key != "jobs_this_month" and key != "jobs_last_month" else 0


def load_from_csv(path: Path) -> BossInput:
    """
    Load from CSV. Two formats:
    - With header: first row = column names (snake_case or spaces), second row = values.
    - No header: single row = revenue_this_month, revenue_last_month, budget_this_month, jobs_this_month, jobs_last_month [, company_name, outstanding_quotes_count, overdue_invoices_count, notes]
    """
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError("CSV file is empty")

    first = rows[0]
    # Check if first row looks like data (first cell is a number)
    try:
        float(str(first[0]).strip().replace(",", ""))
        has_header = False
        data_row = first
    except (ValueError, TypeError, IndexError):
        has_header = True
        data_row = rows[1] if len(rows) > 1 else first

    if has_header:
        headers = [_normalize_header(h) for h in first]
        # Build dict: map header -> value from data_row
        data: dict = {}
        for i, h in enumerate(headers):
            if i < len(data_row):
                val = data_row[i]
                if h in REQUIRED_KEYS or h in OPTIONAL_KEYS:
                    if h in ("company_name", "notes"):
                        data[h] = (val or "").strip() or None
                    elif h in ("outstanding_quotes_count", "overdue_invoices_count"):
                        data[h] = _parse_value(val, h)
                    else:
                        data[h] = _parse_value(val, h)
        for k in REQUIRED_KEYS:
            if k not in data:
                data[k] = 0 if "jobs" in k else 0.0
        if "costs_this_month" not in data:
            data["costs_this_month"] = 0.0
        return BossInput.from_dict(data)
    else:
        # No header: fixed order
        data = {}
        for i, k in enumerate(REQUIRED_KEYS):
            data[k] = _parse_value(data_row[i] if i < len(data_row) else "", k)
        for i, k in enumerate(OPTIONAL_KEYS):
            j = len(REQUIRED_KEYS) + i
            if j < len(data_row):
                data[k] = _parse_value(data_row[j], k)
        return BossInput.from_dict(data)


def get_latest_inbox_file(
    inbox_dir: Path,
    extensions: tuple[str, ...] = (".json", ".csv"),
) -> Optional[Path]:
    """
    Return the path to the newest file in inbox_dir with one of the given extensions (by modification time).
    Returns None if no matching file exists.
    """
    inbox_dir = Path(inbox_dir)
    if not inbox_dir.is_dir():
        return None
    candidates = []
    for ext in extensions:
        candidates.extend(inbox_dir.glob(f"*{ext}"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def load_from_history_csv(path: Path, company_name: Optional[str] = None) -> BossInput:
    """
    Load from a multi-row history CSV: one row per month (oldest first).
    Columns: month, revenue, jobs_completed, budget (or jobs).
    Uses the LAST two rows as "this month" vs "last month" for the report.
    """
    path = Path(path)
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError("History CSV is empty")
    headers = [_normalize_header(h) for h in rows[0]]
    # Map column names to indices (allow revenue, jobs_completed or jobs, budget, costs, month)
    col = {}
    for i, h in enumerate(headers):
        if h in ("revenue", "revenue_this_month"):
            col["revenue"] = i
        if h in ("jobs_completed", "jobs", "jobs_this_month"):
            col["jobs"] = i
        if h in ("budget", "budget_this_month"):
            col["budget"] = i
        if h in ("costs", "costs_this_month"):
            col["costs"] = i
    if "revenue" not in col or "jobs" not in col:
        raise ValueError("History CSV must have 'revenue' and 'jobs_completed' (or 'jobs') columns")
    data_rows = [r for r in rows[1:] if r and any(c.strip() for c in r)]
    if len(data_rows) < 2:
        raise ValueError("History CSV needs at least 2 months of data (two rows after the header)")
    last = data_rows[-1]
    prev = data_rows[-2]
    def val(row: list, key: str) -> float:
        i = col.get(key)
        if i is None or i >= len(row):
            return 0.0 if key != "jobs" else 0
        s = (row[i] or "").strip().replace(",", "")
        if not s:
            return 0.0 if key != "jobs" else 0
        try:
            return float(s) if key != "jobs" else int(float(s))
        except (ValueError, TypeError):
            return 0.0 if key != "jobs" else 0
    budget_this = val(last, "budget") if "budget" in col else val(prev, "budget")
    if budget_this == 0 and "budget" in col:
        budget_this = val(prev, "budget")
    costs_this = val(last, "costs") if "costs" in col else 0.0
    data = {
        "revenue_this_month": val(last, "revenue"),
        "revenue_last_month": val(prev, "revenue"),
        "budget_this_month": budget_this,
        "costs_this_month": costs_this,
        "jobs_this_month": val(last, "jobs"),
        "jobs_last_month": val(prev, "jobs"),
    }
    if company_name:
        data["company_name"] = company_name
    return BossInput.from_dict(data)


def load_from_path(path: Path) -> BossInput:
    """Load from a file; format inferred by extension (.json or .csv)."""
    path = Path(path)
    suf = path.suffix.lower()
    if suf == ".json":
        return load_from_json(path)
    if suf == ".csv":
        return load_from_csv(path)
    raise ValueError(f"Unsupported file type: {suf}. Use .json or .csv")


def load_from_12month_csv(path: Path, company_name: Optional[str] = None) -> BossInput:
    """
    Load from a 12-month (or multi-month) CSV: one row per month.
    Columns: month (YYYY-MM), revenue, budget, jobs (or jobs_completed).
    Rows are sorted by month; the latest month and the previous month are used as this_month and last_month.
    """
    path = Path(path)
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    if not rows:
        raise ValueError("12-month CSV is empty")
    headers = [_normalize_header(h) for h in rows[0]]
    # Map columns: month, revenue, budget, jobs, costs
    col = {}
    for i, h in enumerate(headers):
        if h in ("month", "month_name"):
            col["month"] = i
        if h in ("revenue",):
            col["revenue"] = i
        if h in ("budget",):
            col["budget"] = i
        if h in ("jobs", "jobs_completed"):
            col["jobs"] = i
        if h in ("costs", "costs_this_month"):
            col["costs"] = i
    if "month" not in col or "revenue" not in col or "jobs" not in col:
        raise ValueError("12-month CSV must have columns: month (YYYY-MM), revenue, budget, jobs")
    data_rows = []
    for r in rows[1:]:
        if not r or not any((c or "").strip() for c in r):
            continue
        month_str = (r[col["month"]] or "").strip()
        if not month_str or len(month_str) < 6:
            continue
        try:
            rev = float((r[col["revenue"]] or "0").strip().replace(",", ""))
        except (ValueError, TypeError):
            rev = 0.0
        try:
            bud = float((r[col["budget"]] or "0").strip().replace(",", "")) if "budget" in col and col["budget"] < len(r) else 0.0
        except (ValueError, TypeError):
            bud = 0.0
        try:
            j = int(float((r[col["jobs"]] or "0").strip().replace(",", "")))
        except (ValueError, TypeError):
            j = 0
        try:
            costs = float((r[col["costs"]] or "0").strip().replace(",", "")) if "costs" in col and col["costs"] < len(r) else 0.0
        except (ValueError, TypeError):
            costs = 0.0
        data_rows.append((month_str, rev, bud, j, costs))
    if len(data_rows) < 2:
        raise ValueError("12-month CSV needs at least 2 months of data")
    data_rows.sort(key=lambda x: x[0])
    last = data_rows[-1]
    prev = data_rows[-2]
    data = {
        "revenue_this_month": last[1],
        "revenue_last_month": prev[1],
        "budget_this_month": last[2],
        "jobs_this_month": last[3],
        "jobs_last_month": prev[3],
        "costs_this_month": last[4] if len(last) > 4 else 0.0,
    }
    if company_name:
        data["company_name"] = company_name
    return BossInput.from_dict(data)


def load_from_path_smart(path: Path, company_name: Optional[str] = None) -> BossInput:
    """
    Load from CSV or JSON. For CSV: if it looks like a history file (month column + multiple rows),
    use last two rows as this month vs last month; otherwise use single-report CSV format.
    """
    path = Path(path)
    suf = path.suffix.lower()
    if suf == ".json":
        return load_from_json(path)
    if suf != ".csv":
        raise ValueError(f"Unsupported file type: {suf}. Use .json or .csv")
    rows = list(csv.reader(path.read_text(encoding="utf-8").splitlines()))
    if not rows or len(rows) < 2:
        return load_from_csv(path)
    headers = [_normalize_header(h) for h in rows[0]]
    data_rows = [r for r in rows[1:] if r and any(c.strip() for c in r)]
    has_month_col = any(h in ("month", "month_name") for h in headers)
    if has_month_col and len(data_rows) >= 2:
        return load_from_history_csv(path, company_name=company_name)
    return load_from_csv(path)
