"""
Extract month + revenue (and optionally budget, jobs) from P&L-style PDFs in a directory.
Outputs a 12-month-style CSV and extraction_report.json.
"""
import csv
import re
from pathlib import Path
from typing import Any

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def _extract_text(path: Path) -> str:
    """Extract text from PDF; try pypdf first, then pdfplumber if empty."""
    text = ""
    if PdfReader:
        try:
            reader = PdfReader(path)
            text = "\n".join(
                (p.extract_text() or "").strip() for p in reader.pages
            ).strip()
        except Exception:
            pass
    if not text and pdfplumber:
        try:
            with pdfplumber.open(path) as pdf:
                text = "\n".join(
                    (p.extract_text() or "").strip() for p in pdf.pages
                ).strip()
        except Exception:
            pass
    return text or ""


MONTH_ABBR = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
              "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def _parse_month_from_filename(name: str) -> str | None:
    """Fallback: parse month from filename e.g. 'Profit and Loss Jan 25.pdf' -> 2025-01."""
    m = re.search(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s*['\u2019]?\s*(\d{2,4})\b", name, re.I)
    if m:
        abbr = m.group(0).split()[0][:3].lower()
        year_str = m.group(1)
        year = int(year_str) if len(year_str) == 4 else 2000 + int(year_str)
        month_num = MONTH_ABBR.get(abbr)
        if month_num is not None:
            return f"{year}-{month_num:02d}"
    return None


def _parse_month_from_text(text: str) -> str | None:
    """Try to find a month (YYYY-MM) from P&L text. Prefer 'Month YYYY' or 'YYYY-MM'."""
    # e.g. "July 2025", "June 2025"
    m = re.search(r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})", text, re.I)
    if m:
        month_names = "January February March April May June July August September October November December".split()
        month_str = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)", text, re.I)
        if month_str:
            mn = month_str.group(1).capitalize()
            try:
                month_num = month_names.index(mn) + 1
                return f"{m.group(1)}-{month_num:02d}"
            except ValueError:
                pass
    # e.g. 2025-07
    m = re.search(r"(\d{4})-(\d{2})(?:\D|$)", text)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    return None


def _parse_revenue_from_text(text: str) -> float | None:
    """Find Total Income or Vision Income style line."""
    # e.g. "Total Income $254,451.18" or "Vision Income\t$135,002.80"
    for pattern in [
        r"Total\s+Income\s+[\$\s]*([\d,]+\.?\d*)",
        r"Vision\s+Income\s+[\$\s]*([\d,]+\.?\d*)",
        r"Total\s+Income\s*\$?\s*([\d,]+\.?\d*)",
        r"Vision\s+Income\s*\$?\s*([\d,]+\.?\d*)",
        r"Income\s*\$?\s*([\d,]+\.?\d*)",
    ]:
        m = re.search(pattern, text, re.I)
        if m:
            try:
                return float(m.group(1).replace(",", ""))
            except ValueError:
                continue
    return None


def _parse_budget_from_text(text: str) -> float | None:
    """Optional: find budget if present in PDF."""
    m = re.search(r"Budget\s*\$?\s*([\d,]+\.?\d*)", text, re.I)
    if m:
        try:
            return float(m.group(1).replace(",", ""))
        except ValueError:
            pass
    return None


def _parse_jobs_from_text(text: str) -> int | None:
    """Optional: find job count if present."""
    m = re.search(r"Jobs?\s*(?:completed)?\s*:?\s*(\d+)", text, re.I)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            pass
    return None


def _parse_costs_from_text(text: str) -> float | None:
    """Find Total Cost of Sales + Total Expenses from P&L."""
    total = 0.0
    for pattern in [
        r"Total\s+Cost\s+of\s+Sales\s+[\$\s]*([\d,]+\.?\d*)",
        r"Total\s+Expenses\s+[\$\s]*([\d,]+\.?\d*)",
    ]:
        for m in re.finditer(pattern, text, re.I):
            try:
                total += float(m.group(1).replace(",", ""))
            except ValueError:
                pass
    return total if total > 0 else None


def build_csv_from_pdf_dir(
    pdf_dir: Path,
    out_csv: Path,
    out_report_json: Path | None = None,
) -> dict[str, Any]:
    """
    Scan pdf_dir for PDFs, extract text, parse month/revenue (and budget/jobs if present).
    Write CSV with columns: month, revenue, budget, jobs.
    Write extraction_report.json with per-file summary. Returns report dict.
    """
    pdf_dir = Path(pdf_dir)
    out_csv = Path(out_csv)
    # Prefer P&L files (have revenue); optionally include Balance Sheets if no P&L
    pnl_pdfs = sorted(pdf_dir.glob("Profit*Loss*.pdf")) or sorted(pdf_dir.glob("*P*L*.pdf"))
    other_pdfs = [p for p in pdf_dir.glob("*.pdf") if p not in pnl_pdfs]
    pdfs = sorted(pnl_pdfs) if pnl_pdfs else sorted(other_pdfs)
    rows = []
    report = {"files": [], "rows": [], "out_csv": str(out_csv)}

    for path in pdfs:
        text = _extract_text(path)
        month = _parse_month_from_text(text) or _parse_month_from_filename(path.name)
        revenue = _parse_revenue_from_text(text)
        budget = _parse_budget_from_text(text)
        jobs = _parse_jobs_from_text(text)
        costs = _parse_costs_from_text(text)
        file_summary = {
            "file": path.name,
            "month": month,
            "revenue": revenue,
            "budget": budget,
            "jobs": jobs,
            "costs": costs,
        }
        report["files"].append(file_summary)
        if month is not None:
            row = {
                "month": month,
                "revenue": revenue if revenue is not None else 0,
                "budget": budget if budget is not None else 0,
                "jobs": jobs if jobs is not None else 0,
                "costs": costs if costs is not None else 0,
            }
            rows.append(row)
            report["rows"].append(row)

    # Sort by month and write CSV
    rows.sort(key=lambda r: r["month"])
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["month", "revenue", "budget", "jobs", "costs"])
        w.writeheader()
        w.writerows(rows)

    if out_report_json is not None:
        import json
        out_report_json.parent.mkdir(parents=True, exist_ok=True)
        out_report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    return report
