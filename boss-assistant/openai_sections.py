"""
Sections 2 and 3: Likely Reasons and Boss To-Do List.
Uses OpenAI API (chat completions); prompt includes only the 5 inputs + general construction context.
No made-up facts; numbers come from the computed metrics we pass in.
"""
import os
from typing import Tuple

from analysis import PerformanceMetrics
from input_model import BossInput, format_aud


def _build_context(inp: BossInput, metrics: PerformanceMetrics) -> str:
    """One block of context for the model: inputs and computed facts only."""
    block = f"""Construction company management data (all figures in AUD):

- Revenue this month: {format_aud(inp.revenue_this_month)}
- Revenue last month: {format_aud(inp.revenue_last_month)}
- Budget this month: {format_aud(inp.budget_this_month)}
- Jobs completed this month: {inp.jobs_this_month}
- Jobs completed last month: {inp.jobs_last_month}

Computed:
- Revenue change: {metrics.revenue_change_dollars:+,.2f} ({metrics.revenue_change_pct:+.1f}%)
- Revenue vs budget: {metrics.revenue_vs_budget_dollars:+,.2f} ({metrics.revenue_vs_budget_pct:+.1f}%)
- Jobs change: {metrics.jobs_change:+d} ({metrics.jobs_change_pct:+.1f}%)
- Average job value this month: {format_aud(metrics.avg_job_value_this)} (last month: {format_aud(metrics.avg_job_value_last)}; change {metrics.avg_job_value_change_pct:+.1f}%)
"""
    if inp.outstanding_quotes_count is not None or inp.overdue_invoices_count is not None or inp.notes:
        block += "\nOptional context (use to tailor reasons and to-dos):\n"
        if inp.outstanding_quotes_count is not None:
            block += f"- Outstanding quotes (not yet converted): {inp.outstanding_quotes_count}\n"
        if inp.overdue_invoices_count is not None:
            block += f"- Overdue invoices: {inp.overdue_invoices_count}\n"
        if inp.notes:
            block += f"- Notes: {inp.notes}\n"
    return block


def _system_prompt() -> str:
    return """You are a business analyst for a construction company. You only use the numbers and context provided. Do not invent facts, extra data, or assumptions beyond general construction industry context (e.g. weather, labour, materials, quoting, scheduling, invoicing). Respond in plain text only. Use the exact section headers and format requested."""


def _user_prompt(inp: BossInput, metrics: PerformanceMetrics) -> str:
    context = _build_context(inp, metrics)
    return f"""Based only on the following data and general construction context, produce two sections.

{context}

Section 2 — LIKELY REASONS
List ranked hypotheses (most likely first) for why performance is as it is. Use only the inputs above and general construction knowledge (e.g. fewer jobs, lower average job value, weather, staffing, quote follow-up, pipeline, timing). No made-up facts. Use bullet points. Keep each reason to one or two short sentences.

Section 3 — BOSS TO-DO LIST
List exactly 5 prioritized actions for the boss, written as clear tasks (e.g. "Follow up outstanding quotes", "Chase overdue invoices"). Base these only on the numbers and typical construction priorities. Number them 1 to 5. One line per task, then a short reason in parentheses on the next line if needed.

Output format (plain text):

2) LIKELY REASONS

• ...

3) BOSS TO-DO LIST

1. ...
2. ...
...
"""


def fetch_reasons_and_todos(inp: BossInput, metrics: PerformanceMetrics) -> Tuple[str, str]:
    """
    Call OpenAI API and return (reasons_section_text, todos_section_text).
    Raises if API key missing or call fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "OPENAI_API_KEY is not set. Set it in your environment or a .env file."
        )

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Install the openai package: pip install openai")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": _system_prompt()},
            {"role": "user", "content": _user_prompt(inp, metrics)},
        ],
        temperature=0.3,
    )
    content = (response.choices[0].message.content or "").strip()
    # Split into section 2 and section 3 by "3) BOSS" or similar
    if "3) BOSS" in content.upper() or "3) BOSS TO-DO" in content:
        idx = content.upper().find("3) BOSS")
        reasons = content[:idx].strip()
        todos = content[idx:].strip()
    else:
        # Fallback: treat whole thing as both (e.g. if model merges)
        reasons = content
        todos = "[Could not separate section 3; see full output above.]"
    return reasons, todos
