"""Send emails via Resend."""
import resend

from app.config import RESEND_API_KEY, RESEND_FROM_EMAIL

resend.api_key = RESEND_API_KEY


def send_report_email(to_email: str, subject: str, body_plain: str) -> str | None:
    """Send report email. Returns None on success, error string on failure."""
    try:
        resend.Emails.send({
            "from": RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": body_plain,
        })
        return None
    except Exception as e:
        return str(e)


def send_reply_email(to_email: str, subject: str, body_plain: str, in_reply_to: str | None = None) -> str | None:
    """Send reply (e.g. after inbound email). Optional In-Reply-To for threading."""
    params = {
        "from": RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "text": body_plain,
    }
    if in_reply_to:
        params["headers"] = {"In-Reply-To": in_reply_to}
    try:
        resend.Emails.send(params)
        return None
    except Exception as e:
        return str(e)
