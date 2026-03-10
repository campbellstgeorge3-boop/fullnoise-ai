"""
Run the Boss Assistant using a 12-month (or any multi-month) history CSV.
Uses the LAST two rows as "this month" vs "last month". No need to type numbers in.
"""
import argparse
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from data_loader import load_from_history_csv
from input_model import ValidationError
from report import build_report

ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Boss Assistant from a history CSV (last 2 rows = this month vs last month)."
    )
    parser.add_argument(
        "--file", "-f",
        type=Path,
        default=ROOT / "vision_12months.csv",
        help="Path to history CSV (columns: month, revenue, jobs_completed, budget). Default: vision_12months.csv",
    )
    parser.add_argument(
        "--company",
        type=str,
        default="Vision Constructions",
        help="Company name for the report header.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="No OpenAI call; section 1 only.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Save report to this file instead of printing.",
    )
    args = parser.parse_args()

    path = args.file if args.file.is_absolute() else ROOT / args.file
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        print("Create a CSV with columns: month, revenue, jobs_completed, budget (one row per month, oldest first).", file=sys.stderr)
        print("See vision_12months.example.csv", file=sys.stderr)
        return 1

    try:
        inp = load_from_history_csv(path, company_name=args.company or None)
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    try:
        report = build_report(inp, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error building report: {e}", file=sys.stderr)
        return 1

    if args.out:
        out_path = args.out if args.out.is_absolute() else ROOT / args.out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"Report saved: {out_path}")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
