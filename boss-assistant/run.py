"""
AI Boss Assistant v1 — CLI entry point.
User enters 5 numbers; app outputs a 3-section management report.
Supports: command-line args, JSON file, or interactive prompts.
Use --dry-run to generate report without calling the OpenAI API.
"""
import argparse
import json
import sys
from pathlib import Path

# Load .env if present (for OPENAI_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from input_model import BossInput, ValidationError
from report import build_report


def _get_input_from_args(args: argparse.Namespace) -> BossInput | None:
    if args.revenue_this is not None and args.revenue_last is not None and args.budget is not None and args.jobs_this is not None and args.jobs_last is not None:
        return BossInput.from_args(
            revenue_this=args.revenue_this,
            revenue_last=args.revenue_last,
            budget=args.budget,
            jobs_this=args.jobs_this,
            jobs_last=args.jobs_last,
            company_name=args.company or None,
            outstanding_quotes_count=args.quotes,
            overdue_invoices_count=args.invoices,
            notes=args.notes or "",
        )
    return None


def _get_input_from_file(path: Path) -> BossInput:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return BossInput.from_dict(raw)


def _prompt_float(msg: str) -> float:
    while True:
        try:
            s = input(msg).strip()
            return float(s) if s else 0.0
        except ValueError:
            print("Enter a number.")


def _prompt_int(msg: str) -> int:
    while True:
        try:
            s = input(msg).strip()
            return int(float(s)) if s else 0
        except (ValueError, TypeError):
            print("Enter a whole number.")


def _get_input_interactive() -> BossInput:
    print("Enter the 5 numbers (press Enter for 0):")
    revenue_this = _prompt_float("Revenue this month: ")
    revenue_last = _prompt_float("Revenue last month: ")
    budget = _prompt_float("Budget this month: ")
    jobs_this = _prompt_int("Jobs completed this month: ")
    jobs_last = _prompt_int("Jobs completed last month: ")
    return BossInput.from_args(
        revenue_this=revenue_this,
        revenue_last=revenue_last,
        budget=budget,
        jobs_this=jobs_this,
        jobs_last=jobs_last,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Boss Assistant v1 — management report from 5 numbers (revenue this/last, budget, jobs this/last)."
    )
    parser.add_argument("--revenue-this", type=float, default=None, help="Revenue this month")
    parser.add_argument("--revenue-last", type=float, default=None, help="Revenue last month")
    parser.add_argument("--budget", type=float, default=None, help="Budget this month")
    parser.add_argument("--jobs-this", type=int, default=None, help="Jobs completed this month")
    parser.add_argument("--jobs-last", type=int, default=None, help="Jobs completed last month")
    parser.add_argument("--file", "-f", type=Path, default=None, help="JSON file with the 5 numbers (keys: revenue_this_month, etc.)")
    parser.add_argument("--dry-run", action="store_true", help="Generate report without calling OpenAI (section 1 real; sections 2 & 3 placeholder)")
    parser.add_argument("--company", type=str, default=None, help="Company name for report header (e.g. Vision Constructions)")
    parser.add_argument("--quotes", type=int, default=None, help="Outstanding quotes count (optional)")
    parser.add_argument("--invoices", type=int, default=None, help="Overdue invoices count (optional)")
    parser.add_argument("--notes", type=str, default=None, help="Optional notes for context (e.g. weather, staffing)")
    args = parser.parse_args()

    try:
        if args.file is not None:
            if not args.file.exists():
                print(f"File not found: {args.file}", file=sys.stderr)
                return 1
            inp = _get_input_from_file(args.file)
        else:
            inp = _get_input_from_args(args)
            if inp is None:
                inp = _get_input_interactive()
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Invalid file: {e}", file=sys.stderr)
        return 1

    try:
        report = build_report(inp, dry_run=args.dry_run)
        print(report)
        return 0
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
