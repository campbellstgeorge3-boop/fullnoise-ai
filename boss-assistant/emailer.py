"""
Email delivery for generated reports using Resend.
Uses env: RESEND_API_KEY, REPORT_EMAIL_TO (comma-separated), REPORT_EMAIL_FROM (default onboarding@resend.dev).
Email body uses personalized, facts-only format; full report attached.
"""
import base64
import json
import math
import os
from pathlib import Path
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from utils import BossInput
    from boss_report import PerformanceMetrics

DEFAULT_FROM = "onboarding@resend.dev"
MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def _load_env() -> tuple[str, list[str], str]:
    """Return (api_key, to_list, from_addr)."""
    api_key = (os.environ.get("RESEND_API_KEY") or "").strip()
    to_raw = (os.environ.get("REPORT_EMAIL_TO") or "").strip()
    to_list = [a.strip() for a in to_raw.split(",") if a.strip()]
    from_addr = (os.environ.get("REPORT_EMAIL_FROM") or DEFAULT_FROM).strip()
    return api_key, to_list, from_addr


def _yyyy_mm_to_mmm_yyyy(yyyy_mm: str) -> str:
    """Convert YYYY-MM to MMM YYYY e.g. 2025-01 -> Jan 2025."""
    parts = yyyy_mm.strip().split("-")
    if len(parts) != 2:
        return yyyy_mm
    try:
        y, m = int(parts[0]), int(parts[1])
        if 1 <= m <= 12:
            return f"{MONTH_NAMES[m - 1]} {y}"
    except ValueError:
        pass
    return yyyy_mm


def _fmt_aud(value: float) -> str:
    return f"${value:,.2f} AUD"


def _fmt_aud_signed(value: float) -> str:
    if value >= 0:
        return f"+{_fmt_aud(value)}"
    return f"-{_fmt_aud(abs(value))}"


def _fmt_pct(p: float | None) -> str:
    if p is None:
        return "n/a"
    return f"{p:+.1f}%"


def build_facts_only_email_body(
    inp: "BossInput",
    metrics: "PerformanceMetrics",
    report_month: str | None,
    recipient_first_name: str | None,
) -> str:
    """
    Build a facts-only email body from inputs and metrics.
    No hypotheses, guessing, or words like "possible", "may", "could", "likely", "suggests".
    """
    greeting = f"Hi {recipient_first_name}," if (recipient_first_name and recipient_first_name.strip()) else "Hi there,"

    rev = metrics.revenue_this
    rev_delta = _fmt_aud_signed(metrics.revenue_change_abs)
    rev_pct = _fmt_pct(metrics.revenue_change_pct)
    budget = metrics.budget
    gap = metrics.budget_gap_abs
    jobs = metrics.jobs_this
    costs = inp.costs_this_month
    jobs_delta = int(metrics.jobs_change_abs)
    jobs_pct = _fmt_pct(metrics.jobs_change_pct)
    avg = metrics.avg_revenue_per_job_this_month
    avg_delta = _fmt_aud_signed(metrics.avg_revenue_per_job_change_abs)
    avg_pct = _fmt_pct(metrics.avg_revenue_per_job_change_pct)

    profit = rev - costs if costs > 0 else None
    profit_str = _fmt_aud(profit) if profit is not None else "—"
    margin_str = f"{(100 * profit / rev):.1f}%" if (profit is not None and rev > 0) else "—"
    costs_str = _fmt_aud(costs) if costs > 0 else "—"

    scorecard = f"""**Scorecard**
- Revenue: {_fmt_aud(rev)} ({rev_delta} vs last month)
- Costs: {costs_str}
- Profit: {profit_str} (Margin: {margin_str})
- Jobs: {jobs} ({jobs_delta:+d} vs last month)
- Budget: {_fmt_aud(budget)} (Gap: {_fmt_aud_signed(gap)})
- Avg Revenue / Job: {_fmt_aud(avg)} ({avg_pct} vs last month)"""

    rev_change = metrics.revenue_change_abs
    jobs_change = int(metrics.jobs_change_abs)
    avg_change = metrics.avg_revenue_per_job_change_abs

    what_changed = f"""**What changed (facts)**
- Revenue: {_fmt_aud_signed(rev_change)} ({rev_pct})
- Jobs: {jobs_change:+d} ({jobs_pct})
- Avg / Job: {_fmt_aud_signed(avg_change)} ({avg_pct})"""

    n_jobs_to_close = 0
    if gap < 0 and avg > 0:
        n_jobs_to_close = int(math.ceil(abs(gap) / avg))
    actions = f"""**Actions (next 14 days)**
1) Close +{n_jobs_to_close} average jobs to cover the budget gap
2) Chase overdue invoices
3) Fill the diary back to at least {metrics.jobs_last} jobs
4) Reduce callbacks/rework vs last month"""

    data_needed = "Data Needed Next: quotes sent ($ and count), overdue invoices ($ and count), callbacks/rework count"

    lines = [
        greeting,
        "",
        "Here's your monthly scorecard — facts only.",
        "",
        scorecard,
        "",
        what_changed,
        "",
        actions,
        "",
        data_needed,
        "",
        "Reply to this email with any question about your numbers and we'll email you back. You can also say \"send my report again\" to get a fresh report.",
    ]
    return "\n".join(lines)


def send_report_email(
    content: Union[str, dict],
    report_month: str | None,
    mode: str,
    saved_path: Path | None = None,
    *,
    recipient_first_name: str | None = None,
    facts_only_body: str | None = None,
    email_to: str | list[str] | None = None,
) -> str | None:
    """
    Send the report by email via Resend.
    Uses facts_only_body as email body when provided; otherwise falls back to content.
    Full report file attached when saved_path exists.
    email_to: override recipient(s); otherwise uses REPORT_EMAIL_TO from env.
    """
    api_key, env_to, from_addr = _load_env()
    if not api_key:
        return "Email skipped: RESEND_API_KEY is not set."
    if email_to is not None:
        to_list = [email_to] if isinstance(email_to, str) else list(email_to)
        to_list = [a.strip() for a in to_list if a and str(a).strip()]
    else:
        to_list = env_to
    if not to_list:
        return "Email skipped: REPORT_EMAIL_TO is not set and email_to not provided."

    if report_month and report_month.strip():
        yyyy_mm = report_month.strip()
    else:
        from datetime import datetime
        yyyy_mm = datetime.now().strftime("%Y-%m")
    subject = f"Vision — Monthly Scorecard ({_yyyy_mm_to_mmm_yyyy(yyyy_mm)})"

    if facts_only_body is not None:
        body = facts_only_body
    elif isinstance(content, dict):
        body = json.dumps(content, indent=2, ensure_ascii=False)
    else:
        body = content

    params = {
        "from": from_addr,
        "to": to_list,
        "subject": subject,
        "text": body,
    }

    attachments = []
    if saved_path is not None and Path(saved_path).is_file():
        raw = Path(saved_path).read_bytes()
        b64 = base64.b64encode(raw).decode("ascii")
        attachments.append({"filename": Path(saved_path).name, "content": b64})
    if attachments:
        params["attachments"] = attachments

    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send(params)
        return None
    except Exception as e:
        err_msg = str(e).lower()
        skip_fallback = (os.environ.get("REPORT_SKIP_FALLBACK") or "").strip().lower() in ("1", "true", "yes")
        if skip_fallback:
            return f"Email failed: {e}"
        if "not verified" in err_msg and from_addr != DEFAULT_FROM:
            try:
                params["from"] = DEFAULT_FROM
                resend.Emails.send(params)
                import sys
                print(f"Boss Assistant: Domain {from_addr!r} was rejected by Resend. Sent from {DEFAULT_FROM} instead. Error: {e}", file=sys.stderr)
                return None
            except Exception:
                pass
        return f"Email failed: {e}"


def send_reply_email(
    to_address: str,
    subject: str,
    body_plain: str,
    in_reply_to: str | None = None,
) -> str | None:
    """
    Send a reply email (e.g. from the chat agent). Uses REPORT_EMAIL_FROM.
    If in_reply_to is set (the Message-ID of the email being replied to), the reply
    threads in the recipient's inbox. Returns None on success, error string on failure.
    """
    api_key, _, from_addr = _load_env()
    if not api_key:
        return "RESEND_API_KEY is not set."
    to_addr = (to_address or "").strip()
    if not to_addr:
        return "No recipient address."
    params = {
        "from": from_addr,
        "to": [to_addr],
        "subject": (subject or "Re: Report").strip(),
        "text": (body_plain or "").strip() or "No content.",
    }
    if in_reply_to and (in_reply_to or "").strip():
        params["headers"] = {"In-Reply-To": (in_reply_to or "").strip()}
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send(params)
        return None
    except Exception as e:
        err_msg = str(e).lower()
        if "not verified" in err_msg and from_addr != DEFAULT_FROM:
            try:
                params["from"] = DEFAULT_FROM
                resend.Emails.send(params)
                return None
            except Exception:
                pass
        return f"Email failed: {e}"


def send_abort_alert_email(
    invalid_fields: list[str],
    email_to: str | list[str] | None = None,
) -> None:
    """
    Send a short alert when report is aborted due to incomplete data.
    Uses same env as send_report_email. email_to overrides REPORT_EMAIL_TO when provided.
    """
    api_key, env_to, from_addr = _load_env()
    if not api_key:
        return
    if email_to is not None:
        to_list = [email_to] if isinstance(email_to, str) else list(email_to)
        to_list = [a.strip() for a in to_list if a and str(a).strip()]
    else:
        to_list = env_to
    if not to_list:
        return
    subject = "Vision — Report Aborted (Data Issue)"
    body = (
        "Report not generated due to incomplete data.\n"
        f"Missing/invalid fields: {', '.join(invalid_fields)}"
    )
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({
            "from": from_addr,
            "to": to_list,
            "subject": subject,
            "text": body,
        })
    except Exception:
        pass  # Best-effort; don't fail the CLI


def send_contact_lead(to_email: str, name: str, email: str, message: str) -> str | None:
    """
    Send a contact-form lead to the business owner. Uses Resend and REPORT_EMAIL_FROM.
    Returns None on success, error string on failure.
    """
    api_key, _, from_addr = _load_env()
    if not api_key:
        return "RESEND_API_KEY is not set."
    to_addr = (to_email or "").strip()
    if not to_addr:
        return "No recipient (CONTACT_EMAIL_TO) set."
    name_s = (name or "").strip() or "—"
    email_s = (email or "").strip() or "—"
    msg_s = (message or "").strip() or "—"
    subject = f"Boss Assistant — New lead: {name_s}"
    body = (
        f"New contact form submission:\n\n"
        f"Name: {name_s}\n"
        f"Email: {email_s}\n\n"
        f"Message:\n{msg_s}\n"
    )
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({
            "from": from_addr,
            "to": [to_addr],
            "subject": subject,
            "text": body,
        })
        return None
    except Exception as e:
        return f"Email failed: {e}"


def send_magic_link_email(to_email: str, login_url: str) -> str | None:
    """
    Send a magic-link email for client portal login. Uses Resend and REPORT_EMAIL_FROM.
    Returns None on success, error string on failure.
    """
    api_key, _, from_addr = _load_env()
    if not api_key:
        return "RESEND_API_KEY is not set."
    to_addr = (to_email or "").strip()
    if not to_addr:
        return "No recipient."
    subject = "Boss Assistant — Sign in to your report"
    body = (
        "Click the link below to sign in to your Boss Assistant report.\n\n"
        f"{login_url}\n\n"
        "This link expires in 1 hour. If you didn't request it, you can ignore this email.\n"
    )
    try:
        import resend
        resend.api_key = api_key
        resend.Emails.send({
            "from": from_addr,
            "to": [to_addr],
            "subject": subject,
            "text": body,
        })
        return None
    except Exception as e:
        return f"Email failed: {e}"
