"""Generate report summary using OpenAI from financial numbers."""
from decimal import Decimal

from openai import OpenAI

from app.config import OPENAI_API_KEY

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client

def generate_report_summary(month: str, revenue: Decimal, costs: Decimal, profit: Decimal, jobs: int) -> str:
    prompt = f"""You are a business report assistant. Write a brief (2-4 sentences) summary for the month {month}.
Numbers: Revenue ${revenue:,.2f}, Costs ${costs:,.2f}, Profit ${profit:,.2f}, Jobs {jobs}.
Use plain English. No bullet points."""
    try:
        r = _get_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
        )
        return (r.choices[0].message.content or "").strip() or f"Summary for {month}: Revenue ${revenue:,.2f}, Profit ${profit:,.2f}."
    except Exception:
        return f"Summary for {month}: Revenue ${revenue:,.2f}, Profit ${profit:,.2f}, Jobs {jobs}."
