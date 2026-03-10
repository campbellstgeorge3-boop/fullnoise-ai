"""
Trigger Resend to re-verify mail.fullnoises.com via the API.
Sometimes the dashboard shows "Verified" but the send API still rejects the domain;
calling the verify API can sync the state. Run from boss-assistant folder with venv active.
"""
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

def main():
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    if not api_key:
        print("RESEND_API_KEY not set in .env", file=sys.stderr)
        return 1
    try:
        import resend
        resend.api_key = api_key
    except ImportError:
        print("Install resend: pip install resend", file=sys.stderr)
        return 1

    # List domains and find mail.fullnoises.com
    resp = resend.Domains.list()
    data = getattr(resp, "data", None) or []
    if isinstance(resp, dict):
        data = resp.get("data") or []
    domain_id = None
    for d in data:
        name = (getattr(d, "name", None) or (d.get("name") if isinstance(d, dict) else None) or "").strip()
        if name == "mail.fullnoises.com":
            domain_id = getattr(d, "id", None) or (d.get("id") if isinstance(d, dict) else None)
            break
    if not domain_id:
        print("Domain mail.fullnoises.com not found in Resend. Add it at https://resend.com/domains", file=sys.stderr)
        return 1

    print(f"Found domain id: {domain_id}. Calling verify API...")
    result = resend.Domains.verify(domain_id)
    status = getattr(result, "status", None) or (result.get("status") if isinstance(result, dict) else "?")
    print(f"Verify API returned. Status: {status}")
    print("Wait a minute, then run: python main.py --run-client default")
    return 0

if __name__ == "__main__":
    sys.exit(main())
