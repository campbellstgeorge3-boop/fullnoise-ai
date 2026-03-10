"""
AI Boss Assistant — Automated run (no prompts).
Reads config; loads data from a file or from the inbox folder (newest file).
Builds report, writes to output_dir with timestamp.
Use with Windows Task Scheduler so it runs by itself. No manual data entry if you use inbox + export.
Use --open to open the report file after it's written (so you see the result).
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Load .env if present (for OPENAI_API_KEY)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from input_model import ValidationError
from report import build_report
from data_loader import get_latest_inbox_file, load_from_path_smart
from api_loader import load_from_api
from myob_loader import load_from_myob_config
from google_loader import load_from_googledrive_config

ROOT = Path(__file__).resolve().parent
DEFAULT_AUTO_CONFIG = ROOT / "auto_config.json"


def _parse_args():
    open_report = "--open" in sys.argv or "-o" in sys.argv
    return open_report


def load_auto_config(path: Path | None = None) -> dict:
    """Load automation config. Paths in config are relative to boss-assistant root."""
    config_path = path or DEFAULT_AUTO_CONFIG
    if not config_path.exists():
        raise FileNotFoundError(
            f"Automation config not found: {config_path}. "
            "Copy auto_config.example.json to auto_config.json and set data_source, output_dir, and data_file or inbox_dir."
        )
    return json.loads(config_path.read_text(encoding="utf-8"))


def main() -> int:
    open_after = _parse_args()
    try:
        config = load_auto_config()
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1

    if open_after:
        config["open_after_write"] = True
    data_source = config.get("data_source", "file")
    data_file = Path(config.get("data_file", "data.json"))
    inbox_dir = Path(config.get("inbox_dir", "inbox"))
    output_dir = Path(config.get("output_dir", "reports"))
    dry_run = bool(config.get("dry_run", False))
    company_name = config.get("company_name") or None

    if not data_file.is_absolute():
        data_file = ROOT / data_file
    if not inbox_dir.is_absolute():
        inbox_dir = ROOT / inbox_dir
    if not output_dir.is_absolute():
        output_dir = ROOT / output_dir

    # Resolve data source and load input
    if data_source == "myob":
        print("Fetching data from MYOB...", file=sys.stderr)
        try:
            inp = load_from_myob_config(config)
        except ValidationError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"MYOB error: {e}", file=sys.stderr)
            return 1
    elif data_source == "googledrive":
        print("Fetching data from Google Drive...", file=sys.stderr)
        try:
            inp = load_from_googledrive_config(config)
        except ValidationError as e:
            print(f"Validation error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Google Drive error: {e}", file=sys.stderr)
            return 1
    elif data_source == "api":
        api_url = config.get("api_url")
        if not api_url:
            print("data_source is 'api' but api_url is missing in auto_config.json", file=sys.stderr)
            return 1
        print(f"Fetching data from API: {api_url}", file=sys.stderr)
        try:
            inp = load_from_api(
                api_url,
                headers=config.get("api_headers"),
                api_key_env=config.get("api_key_env"),
                company_name=company_name,
            )
        except ValidationError as e:
            print(f"Validation error in API response: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"API error: {e}", file=sys.stderr)
            return 1
    elif data_source == "inbox":
        source_path = get_latest_inbox_file(inbox_dir)
        if source_path is None:
            print(f"No .json or .csv file found in inbox: {inbox_dir}", file=sys.stderr)
            print("Drop or export a JSON/CSV file into the inbox folder; the newest file is used.", file=sys.stderr)
            return 1
        print(f"Using latest file: {source_path}", file=sys.stderr)
        try:
            inp = load_from_path_smart(source_path, company_name=company_name)
        except ValidationError as e:
            print(f"Validation error in data: {e}", file=sys.stderr)
            return 1
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Invalid data file: {e}", file=sys.stderr)
            return 1
    else:
        if not data_file.exists():
            print(f"Data file not found: {data_file}", file=sys.stderr)
            print("Update data.json (or set data_file in auto_config.json). Or use data_source: 'inbox', 'api', 'googledrive', or 'myob'.", file=sys.stderr)
            return 1
        source_path = data_file
        try:
            inp = load_from_path_smart(source_path, company_name=company_name)
        except ValidationError as e:
            print(f"Validation error in data: {e}", file=sys.stderr)
            return 1
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Invalid data file: {e}", file=sys.stderr)
            return 1

    try:
        report = build_report(inp, dry_run=dry_run)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error building report: {e}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    out_file = output_dir / f"report_{timestamp}.txt"
    out_file.write_text(report, encoding="utf-8")
    print(f"Report written: {out_file}")

    if config.get("open_after_write", False):
        try:
            os.startfile(out_file)
        except Exception:
            print(f"Open the report manually: {out_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
