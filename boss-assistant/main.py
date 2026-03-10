# -----------------------------------------------------------------------------
# main.py — Entry point for the AI Boss Assistant.
# -----------------------------------------------------------------------------
"""
CLI: interactive prompts (friendly, commas allowed) or flag-based mode.
Usage:
  python main.py                    # interactive: prompt for inputs, then text/json and dry-run
  python main.py --text             # flag mode: prompt for inputs only, output text
  python main.py --json             # flag mode: output JSON
  python main.py --dry-run          # flag mode: skip API, show placeholders
  python main.py -f data.json --text
"""

import argparse
import json
import sys
from pathlib import Path

# Load .env for OPENAI_API_KEY if present
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from utils import BossInput, ValidationError, parse_from_dict, validate_and_parse
from boss_report import ERROR_PREFIX, generate_report


def _parse_number(s: str) -> float:
    """Parse a number string; allow commas (e.g. 120,000). Raises ValueError if invalid or negative."""
    cleaned = (s or "").strip().replace(",", "")
    if not cleaned:
        return 0.0
    val = float(cleaned)
    if val < 0:
        raise ValueError("Value must be non-negative.")
    return val


def _prompt_float(msg: str) -> float:
    """Prompt until user enters a valid non-negative number (commas allowed)."""
    while True:
        try:
            s = input(msg).strip()
            return _parse_number(s) if s else 0.0
        except ValueError as e:
            print(f"  Invalid: {e}. Try again (e.g. 185000 or 185,000).")


def _prompt_int(msg: str) -> int:
    """Prompt until user enters a valid non-negative integer (commas allowed)."""
    while True:
        try:
            s = input(msg).strip()
            if not s:
                return 0
            val = int(_parse_number(s))
            return val
        except ValueError as e:
            print(f"  Invalid: {e}. Try again (e.g. 12).")


def _get_input_interactive() -> BossInput:
    """Ask for each input with friendly prompts; accept commas; validate non-negative."""
    print("\n--- Vision Constructions — Monthly inputs ---\n")
    while True:
        try:
            inp = validate_and_parse(
                revenue_this_month=_prompt_float("Revenue this month (AUD)? "),
                revenue_last_month=_prompt_float("Revenue last month (AUD)? "),
                budget_this_month=_prompt_float("Budget this month (AUD)? "),
                jobs_this_month=_prompt_int("Jobs completed this month? "),
                jobs_last_month=_prompt_int("Jobs completed last month? "),
            )
            return inp
        except ValidationError as e:
            print(f"  {e}. Please enter non-negative numbers only.\n")


def _get_input_from_args(args: argparse.Namespace) -> BossInput | None:
    """Build BossInput from CLI args if all five are provided."""
    if all(
        getattr(args, k) is not None
        for k in ("revenue_this", "revenue_last", "budget", "jobs_this", "jobs_last")
    ):
        return validate_and_parse(
            revenue_this_month=args.revenue_this,
            revenue_last_month=args.revenue_last,
            budget_this_month=args.budget,
            jobs_this_month=args.jobs_this,
            jobs_last_month=args.jobs_last,
        )
    return None


def _get_input_from_file(path: Path) -> BossInput:
    """Load JSON and parse into BossInput; strip commas from string numbers in file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    # Allow commas in numeric strings from file
    for key in ("revenue_this_month", "revenue_last_month", "budget_this_month"):
        if key in raw and isinstance(raw[key], str):
            raw[key] = float(raw[key].replace(",", ""))
    for key in ("jobs_this_month", "jobs_last_month"):
        if key in raw and isinstance(raw[key], str):
            raw[key] = int(float(raw[key].replace(",", "")))
    return parse_from_dict(raw)


def _ask_output_mode() -> str:
    """Ask user for text or json. Returns 'text' or 'json'."""
    while True:
        s = input("Output as text or JSON? (t/j) [t]: ").strip().lower() or "t"
        if s in ("t", "text"):
            return "text"
        if s in ("j", "json"):
            return "json"
        print("  Enter t for text or j for JSON.")


def _ask_dry_run() -> bool:
    """Ask user for dry run. Returns True or False."""
    while True:
        s = input("Dry run (skip API call)? (y/n) [n]: ").strip().lower() or "n"
        if s in ("y", "yes"):
            return True
        if s in ("n", "no"):
            return False
        print("  Enter y or n.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AI Boss Assistant — management report from 5 numbers (revenue this/last, budget, jobs this/last)."
    )
    parser.add_argument("--revenue-this", type=float, default=None, help="Revenue this month (commas allowed in interactive)")
    parser.add_argument("--revenue-last", type=float, default=None, help="Revenue last month")
    parser.add_argument("--budget", type=float, default=None, help="Budget this month")
    parser.add_argument("--jobs-this", type=int, default=None, help="Jobs completed this month")
    parser.add_argument("--jobs-last", type=int, default=None, help="Jobs completed last month")
    parser.add_argument("--file", "-f", type=Path, default=None, help="JSON file with the 5 numbers")
    parser.add_argument("--dry-run", action="store_true", help="Skip OpenAI call; show placeholders")
    parser.add_argument("--text", action="store_true", help="Output full report as text")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output report as JSON")
    args = parser.parse_args()

    # Resolve output mode from flags
    if args.json_output:
        output_mode = "json"
    elif args.text:
        output_mode = "text"
    else:
        output_mode = None  # ask in interactive

    # Resolve dry_run from flag
    dry_run_flag_set = args.dry_run

    # Get input: file, then args, then interactive
    try:
        if args.file is not None:
            if not args.file.exists():
                print(f"File not found: {args.file}", file=sys.stderr)
                return 1
            inp = _get_input_from_file(args.file)
            asked_interactive = False
        else:
            inp = _get_input_from_args(args)
            if inp is None:
                inp = _get_input_interactive()
                asked_interactive = True
            else:
                asked_interactive = False
    except ValidationError as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Invalid file: {e}", file=sys.stderr)
        return 1

    # If we prompted for numbers, also ask output mode and dry run unless set by flags
    if asked_interactive:
        if output_mode is None:
            output_mode = _ask_output_mode()
        if not dry_run_flag_set:
            dry_run = _ask_dry_run()
        else:
            dry_run = True
    else:
        if output_mode is None:
            output_mode = "text"
        dry_run = dry_run_flag_set

    print()
    try:
        report = generate_report(inp, dry_run=dry_run, output_mode=output_mode)
        if isinstance(report, str) and report.startswith(ERROR_PREFIX):
            print(report[len(ERROR_PREFIX):], file=sys.stderr)
            return 1
        if isinstance(report, dict):
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
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
