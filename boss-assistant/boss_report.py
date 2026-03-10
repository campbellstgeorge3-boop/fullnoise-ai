# -----------------------------------------------------------------------------
# boss_report.py — Logic for computing metrics and calling the OpenAI model.
# -----------------------------------------------------------------------------
"""Compute performance metrics, build section 1, call the model for sections 2 & 3, return full report."""

import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

from utils import BossInput, format_aud, format_aud_signed
from prompts import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
    USER_PROMPT_JSON_TEMPLATE,
)


# -----------------------------------------------------------------------------
# Metrics computation
# -----------------------------------------------------------------------------

@dataclass
class PerformanceMetrics:
    """Computed performance metrics from the five inputs. Floats internally; format later. Pct fields are None when denominator is 0."""
    revenue_change_abs: float
    revenue_change_pct: Optional[float]
    budget_gap_abs: float
    budget_gap_pct: Optional[float]
    jobs_change_abs: float
    jobs_change_pct: Optional[float]
    avg_revenue_per_job_this_month: float
    avg_revenue_per_job_last_month: float
    avg_revenue_per_job_change_abs: float
    avg_revenue_per_job_change_pct: Optional[float]
    # Keep these for summary/context (raw inputs and budget)
    revenue_this: float
    revenue_last: float
    budget: float
    jobs_this: int
    jobs_last: int


def _pct_or_none(current: float, previous: float) -> Optional[float]:
    """Return 100 * (current - previous) / previous, or None if previous == 0."""
    if previous == 0:
        return None
    return float(100 * (current - previous) / previous)


def _avg_revenue_per_job(revenue: float, jobs: int) -> float:
    """Average revenue per job; 0.0 if jobs <= 0."""
    if jobs <= 0:
        return 0.0
    return float(revenue / jobs)


def compute_metrics(inputs: BossInput) -> PerformanceMetrics:
    """
    Compute all performance metrics from the five inputs.
    Uses floats internally; format later. Returns None for any pct where denominator is 0.
    """
    rev_this = float(inputs.revenue_this_month)
    rev_last = float(inputs.revenue_last_month)
    budget = float(inputs.budget_this_month)
    jobs_this = int(inputs.jobs_this_month)
    jobs_last = int(inputs.jobs_last_month)

    revenue_change_abs = rev_this - rev_last
    revenue_change_pct = _pct_or_none(rev_this, rev_last)

    budget_gap_abs = rev_this - budget
    budget_gap_pct = _pct_or_none(rev_this, budget) if budget != 0 else None

    jobs_change_abs = float(jobs_this - jobs_last)
    jobs_change_pct = _pct_or_none(float(jobs_this), float(jobs_last))

    avg_this = _avg_revenue_per_job(rev_this, jobs_this)
    avg_last = _avg_revenue_per_job(rev_last, jobs_last)
    avg_revenue_per_job_change_abs = avg_this - avg_last
    avg_revenue_per_job_change_pct = _pct_or_none(avg_this, avg_last)

    return PerformanceMetrics(
        revenue_change_abs=revenue_change_abs,
        revenue_change_pct=revenue_change_pct,
        budget_gap_abs=budget_gap_abs,
        budget_gap_pct=budget_gap_pct,
        jobs_change_abs=jobs_change_abs,
        jobs_change_pct=jobs_change_pct,
        avg_revenue_per_job_this_month=avg_this,
        avg_revenue_per_job_last_month=avg_last,
        avg_revenue_per_job_change_abs=avg_revenue_per_job_change_abs,
        avg_revenue_per_job_change_pct=avg_revenue_per_job_change_pct,
        revenue_this=rev_this,
        revenue_last=rev_last,
        budget=budget,
        jobs_this=jobs_this,
        jobs_last=jobs_last,
    )


# -----------------------------------------------------------------------------
# Self-check / unit tests (run with: python -m boss_assistant.boss_report)
# -----------------------------------------------------------------------------

def run_self_check() -> bool:
    """Run quick sanity checks on compute_metrics. Returns True if all pass."""
    from utils import validate_and_parse

    ok = True

    # Normal case
    inp = validate_and_parse(185000, 210000, 200000, 12, 14)
    m = compute_metrics(inp)
    assert m.revenue_change_abs == -25000.0, m.revenue_change_abs
    assert m.revenue_change_pct is not None and abs(m.revenue_change_pct - (-11.904761904761905)) < 0.01
    assert m.budget_gap_abs == -15000.0
    assert m.budget_gap_pct is not None and abs(m.budget_gap_pct - (-7.5)) < 0.01
    assert m.jobs_change_abs == -2.0
    assert m.jobs_change_pct is not None and abs(m.jobs_change_pct - (-14.285714285714285)) < 0.01
    assert m.avg_revenue_per_job_this_month == 185000 / 12
    assert m.avg_revenue_per_job_last_month == 210000 / 14
    assert m.avg_revenue_per_job_change_abs == (185000 / 12) - (210000 / 14)
    assert m.avg_revenue_per_job_change_pct is not None
    print("OK: normal case")

    # Divide-by-zero: last month revenue 0
    inp_zero_rev = validate_and_parse(100, 0, 50, 2, 1)
    m2 = compute_metrics(inp_zero_rev)
    assert m2.revenue_change_pct is None, "revenue_change_pct should be None when rev_last=0"
    print("OK: revenue_change_pct None when rev_last=0")

    # Divide-by-zero: budget 0
    inp_zero_budget = validate_and_parse(100, 80, 0, 2, 2)
    m3 = compute_metrics(inp_zero_budget)
    assert m3.budget_gap_pct is None, "budget_gap_pct should be None when budget=0"
    print("OK: budget_gap_pct None when budget=0")

    # Divide-by-zero: jobs last month 0
    inp_zero_jobs = validate_and_parse(100, 0, 0, 5, 0)
    m4 = compute_metrics(inp_zero_jobs)
    assert m4.jobs_change_pct is None
    assert m4.avg_revenue_per_job_last_month == 0.0
    assert m4.avg_revenue_per_job_change_pct is None, "avg_revenue_per_job_change_pct should be None when avg_last=0"
    print("OK: jobs and avg pct None when denominator 0")

    # All zeros
    inp_all_zero = validate_and_parse(0, 0, 0, 0, 0)
    m5 = compute_metrics(inp_all_zero)
    assert m5.revenue_change_pct is None
    assert m5.budget_gap_pct is None
    assert m5.jobs_change_pct is None
    assert m5.avg_revenue_per_job_this_month == 0.0
    assert m5.avg_revenue_per_job_last_month == 0.0
    assert m5.avg_revenue_per_job_change_pct is None
    print("OK: all zeros")

    return ok


# -----------------------------------------------------------------------------
# Section 1: Performance Summary (computed in code)
# -----------------------------------------------------------------------------

def _fmt_pct(p: Optional[float]) -> str:
    if p is None:
        return "n/a"
    return f"{p:+.1f}%"


def _build_performance_summary(metrics: PerformanceMetrics) -> str:
    """Build section 1 as plain text with bullet points and AUD formatting."""
    lines = [
        "1) PERFORMANCE SUMMARY",
        "",
        f"• Revenue this month: {format_aud(metrics.revenue_this)}",
        f"• Revenue last month: {format_aud(metrics.revenue_last)}",
        f"• Revenue change: {format_aud_signed(metrics.revenue_change_abs)} ({_fmt_pct(metrics.revenue_change_pct)})",
        "",
    ]
    if metrics.budget != 0:
        lines.extend([
            f"• Budget this month: {format_aud(metrics.budget)}",
            f"• Revenue vs budget: {format_aud_signed(metrics.budget_gap_abs)} ({_fmt_pct(metrics.budget_gap_pct)})",
            "",
        ])
    lines.extend([
        f"• Jobs completed this month: {metrics.jobs_this}",
        f"• Jobs completed last month: {metrics.jobs_last}",
        f"• Jobs change: {int(metrics.jobs_change_abs):+d} ({_fmt_pct(metrics.jobs_change_pct)})",
        "",
    ])
    if metrics.jobs_this > 0 or metrics.jobs_last > 0:
        lines.extend([
            f"• Average revenue per job this month: {format_aud(metrics.avg_revenue_per_job_this_month)}",
            f"• Average revenue per job last month: {format_aud(metrics.avg_revenue_per_job_last_month)}",
            f"• Average revenue per job change: {format_aud_signed(metrics.avg_revenue_per_job_change_abs)} ({_fmt_pct(metrics.avg_revenue_per_job_change_pct)})",
            "",
        ])
    return "\n".join(lines)


# -----------------------------------------------------------------------------
# Context block for the user prompt (injected into USER_PROMPT_TEMPLATE)
# -----------------------------------------------------------------------------

# Model and request settings — use "gpt-5" when available in your account
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 4096

# Prefix for error returns so callers can detect failure without parsing
ERROR_PREFIX = "[Error] "


def _build_context_block(inp: BossInput, metrics: PerformanceMetrics) -> str:
    """Build the context block with inputs and computed metrics for the model."""
    return f"""Construction company management data (all figures in AUD):

- Revenue this month: {format_aud(inp.revenue_this_month)}
- Revenue last month: {format_aud(inp.revenue_last_month)}
- Budget this month: {format_aud(inp.budget_this_month)}
- Jobs completed this month: {inp.jobs_this_month}
- Jobs completed last month: {inp.jobs_last_month}

Computed:
- Revenue change: {format_aud_signed(metrics.revenue_change_abs)} ({_fmt_pct(metrics.revenue_change_pct)})
- Revenue vs budget: {format_aud_signed(metrics.budget_gap_abs)} ({_fmt_pct(metrics.budget_gap_pct)})
- Jobs change: {int(metrics.jobs_change_abs):+d} ({_fmt_pct(metrics.jobs_change_pct)})
- Average revenue per job this month: {format_aud(metrics.avg_revenue_per_job_this_month)} (last month: {format_aud(metrics.avg_revenue_per_job_last_month)}; change {_fmt_pct(metrics.avg_revenue_per_job_change_pct)})
"""


# -----------------------------------------------------------------------------
# OpenAI Responses API — call_model_report
# -----------------------------------------------------------------------------

def _safe_parse_json(raw: str) -> Union[Dict[str, Any], str]:
    """Parse JSON from model output; strip markdown fences. Return dict or ERROR_PREFIX string."""
    s = raw.strip()
    if s.startswith("```"):
        # Remove ```json or ``` and trailing ```
        s = re.sub(r"^```(?:json)?\s*", "", s)
        s = re.sub(r"\s*```\s*$", "", s)
        s = s.strip()
    try:
        obj = json.loads(s)
    except json.JSONDecodeError as e:
        return f"{ERROR_PREFIX}Invalid JSON from model: {e}"
    if not isinstance(obj, dict):
        return f"{ERROR_PREFIX}Model did not return a JSON object."
    return obj


def call_model_report(
    inputs: BossInput,
    metrics: PerformanceMetrics,
    output_mode: Literal["text", "json"] = "text",
    *,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = MAX_OUTPUT_TOKENS,
) -> Union[str, Dict[str, Any]]:
    """
    Call the OpenAI Responses API (chat completions) to generate the report.

    - output_mode "text": uses the full text prompt; returns the report string (or an error string starting with [Error]).
    - output_mode "json": uses the JSON prompt; returns a dict with title, summary_bullets, reasons_bullets, todo_items, data_needed_next_month (or an error string).

    Handles network and API errors gracefully. Never logs or exposes the API key.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or not api_key.strip():
        return f"{ERROR_PREFIX}OPENAI_API_KEY is not set. Set it in your environment or a .env file."

    context_block = _build_context_block(inputs, metrics)
    if output_mode == "text":
        user_content = USER_PROMPT_TEMPLATE.format(context_block=context_block)
    else:
        user_content = USER_PROMPT_JSON_TEMPLATE.format(context_block=context_block)

    try:
        from openai import OpenAI
    except ImportError:
        return f"{ERROR_PREFIX}OpenAI package not installed. Run: pip install openai"

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception as e:
        err_msg = str(e).strip()
        # Never log or expose the API key
        if not err_msg or "sk-" in err_msg or "api_key" in err_msg.lower() or "api key" in err_msg.lower():
            err_msg = "API request failed (check your key and network)."
        else:
            err_msg = re.sub(r"sk-[a-zA-Z0-9]+", "[REDACTED]", err_msg)
        return f"{ERROR_PREFIX}Network or API error: {err_msg}"

    content = (response.choices[0].message.content or "").strip()
    if not content:
        return f"{ERROR_PREFIX}Model returned empty content."

    if output_mode == "json":
        parsed = _safe_parse_json(content)
        if isinstance(parsed, str):
            return parsed
        # Ensure expected keys exist (with safe defaults)
        return {
            "title": parsed.get("title", "Vision Constructions — Monthly Performance Report"),
            "summary_bullets": parsed.get("summary_bullets") if isinstance(parsed.get("summary_bullets"), list) else [],
            "reasons_bullets": parsed.get("reasons_bullets") if isinstance(parsed.get("reasons_bullets"), list) else [],
            "todo_items": parsed.get("todo_items") if isinstance(parsed.get("todo_items"), list) else [],
            "data_needed_next_month": parsed.get("data_needed_next_month") if isinstance(parsed.get("data_needed_next_month"), str) else "",
        }

    return content


# -----------------------------------------------------------------------------
# Dry-run report (deterministic, no AI)
# -----------------------------------------------------------------------------

DRY_RUN_LABEL = " (Generated without AI — Dry Run)"


def _dry_run_performance_bullets(metrics: PerformanceMetrics) -> List[str]:
    """Build 4–7 performance summary bullets from threshold rules."""
    bullets = []
    # Revenue level
    bullets.append(f"Revenue this month is {format_aud(metrics.revenue_this)} (last month: {format_aud(metrics.revenue_last)}).")
    # Revenue change
    if metrics.revenue_change_pct is not None:
        if metrics.revenue_change_pct < -10:
            bullets.append(f"Revenue is down {abs(metrics.revenue_change_pct):.1f}% on last month ({format_aud_signed(metrics.revenue_change_abs)}).")
        elif metrics.revenue_change_pct > 10:
            bullets.append(f"Revenue is up {metrics.revenue_change_pct:.1f}% on last month ({format_aud_signed(metrics.revenue_change_abs)}).")
        else:
            bullets.append(f"Revenue change is {_fmt_pct(metrics.revenue_change_pct)} versus last month.")
    # Budget
    if metrics.budget > 0:
        if metrics.budget_gap_abs < 0:
            bullets.append(f"Revenue is below budget by {format_aud(abs(metrics.budget_gap_abs))} (budget: {format_aud(metrics.budget)}).")
        elif metrics.budget_gap_abs > 0:
            bullets.append(f"Revenue is above budget by {format_aud(metrics.budget_gap_abs)}.")
        else:
            bullets.append("Revenue is on budget this month.")
    # Jobs
    bullets.append(f"Jobs completed: {metrics.jobs_this} this month, {metrics.jobs_last} last month ({int(metrics.jobs_change_abs):+d} change).")
    if metrics.jobs_change_pct is not None and abs(metrics.jobs_change_pct) >= 10:
        bullets.append(f"Job count has moved {_fmt_pct(metrics.jobs_change_pct)} compared to last month.")
    # Average job value
    if metrics.jobs_this > 0 and metrics.jobs_last > 0:
        bullets.append(f"Average revenue per job: {format_aud(metrics.avg_revenue_per_job_this_month)} this month, {format_aud(metrics.avg_revenue_per_job_last_month)} last month.")
        if metrics.avg_revenue_per_job_change_pct is not None and abs(metrics.avg_revenue_per_job_change_pct) >= 5:
            bullets.append(f"Average job value has changed by {_fmt_pct(metrics.avg_revenue_per_job_change_pct)}.")
    return bullets[:7]  # cap at 7


def _dry_run_reasons_bullets(metrics: PerformanceMetrics) -> List[str]:
    """Generic construction-relevant likely reasons from thresholds."""
    reasons = []
    if metrics.revenue_change_pct is not None and metrics.revenue_change_pct < -10:
        reasons.append("Possible impact from fewer jobs completed or slower project progress (common in construction when weather, labour, or materials delay work).")
    if metrics.budget_gap_abs < 0 and metrics.budget > 0:
        reasons.append("Possible shortfall against plan due to delayed starts, quote conversion, or timing of invoicing.")
    if metrics.jobs_change_abs < 0 and metrics.jobs_last > 0:
        reasons.append("Possible effect of resourcing, scheduling, or site access limiting how many jobs could be finished this month.")
    if metrics.avg_revenue_per_job_change_pct is not None and metrics.avg_revenue_per_job_change_pct < -5 and metrics.avg_revenue_per_job_last_month > 0:
        reasons.append("Possible shift toward smaller or lower-margin jobs, or different mix of work.")
    if metrics.revenue_change_pct is not None and metrics.revenue_change_pct > 10:
        reasons.append("Stronger month may reflect more jobs completed, better conversion of quotes, or favourable timing of completions.")
    if not reasons:
        reasons.append("No major swings this month; performance is broadly in line with last month.")
    return reasons[:6]  # cap at 6


def _dry_run_todo_items(metrics: PerformanceMetrics) -> List[str]:
    """Five to-do items consistent with detected issues (verb-first, reason in parentheses)."""
    todos = []
    if metrics.revenue_change_pct is not None and metrics.revenue_change_pct < -10:
        todos.append("Follow up outstanding quotes (to convert pipeline and lock in start dates).")
    if metrics.budget_gap_abs < 0 and metrics.budget > 0:
        todos.append("Review pipeline and pre-book work where possible (to close the gap to budget).")
    if metrics.jobs_change_abs < 0:
        todos.append("Check resourcing and scheduling bottlenecks (to avoid further delays next month).")
    if metrics.avg_revenue_per_job_change_pct is not None and metrics.avg_revenue_per_job_change_pct < -5:
        todos.append("Focus sales and quoting on higher-value jobs (to improve average job value).")
    todos.append("Chase overdue invoices (to improve cash flow).")
    # Fill to 5 if needed
    generic = [
        "Schedule a short planning session with the team (to align on priorities for next month).",
        "Review key supplier and subcontractor lead times (to reduce delays).",
        "Update job pipeline and quote log (to track conversion and forecast).",
    ]
    while len(todos) < 5:
        for g in generic:
            if g not in todos:
                todos.append(g)
                break
        else:
            todos.append("Review monthly KPIs and adjust targets if needed (to stay on track).")
            break
    return todos[:5]


def dry_run_report(inputs: BossInput, metrics: PerformanceMetrics) -> str:
    """
    Generate the same 3 sections using deterministic rules (no API call).
    Reads like a real report but is clearly labelled (Generated without AI — Dry Run).
    """
    title = f"Vision Constructions — Monthly Performance Report{DRY_RUN_LABEL}"
    summary_bullets = _dry_run_performance_bullets(metrics)
    reasons_bullets = _dry_run_reasons_bullets(metrics)
    todo_items = _dry_run_todo_items(metrics)
    data_needed = "Track outstanding quote values and overdue invoice amounts next month to improve forecasts."

    lines = [
        title,
        "",
        "1) Performance Summary",
        "",
    ]
    for b in summary_bullets:
        lines.append(f"• {b}")
    lines.extend([
        "",
        "2) Likely Reasons (Hypotheses)",
        "",
    ])
    for r in reasons_bullets:
        lines.append(f"• {r}")
    lines.extend([
        "",
        "3) Boss To-Do List (Next 30 Days)",
        "",
    ])
    for i, t in enumerate(todo_items, 1):
        lines.append(f"{i}. {t}")
    lines.extend([
        "",
        f"Data Needed Next Month: {data_needed}",
    ])
    return "\n".join(lines)


def dry_run_report_json(inputs: BossInput, metrics: PerformanceMetrics) -> Dict[str, Any]:
    """Same content as dry_run_report but as a structured dict for JSON output."""
    summary_bullets = _dry_run_performance_bullets(metrics)
    reasons_bullets = _dry_run_reasons_bullets(metrics)
    todo_items = _dry_run_todo_items(metrics)
    data_needed = "Track outstanding quote values and overdue invoice amounts next month to improve forecasts."
    return {
        "title": f"Vision Constructions — Monthly Performance Report{DRY_RUN_LABEL}",
        "summary_bullets": summary_bullets,
        "reasons_bullets": reasons_bullets,
        "todo_items": todo_items,
        "data_needed_next_month": data_needed,
    }


# -----------------------------------------------------------------------------
# Full report
# -----------------------------------------------------------------------------


def generate_report(
    inp: BossInput,
    dry_run: bool = False,
    output_mode: Literal["text", "json"] = "text",
) -> Union[str, Dict[str, Any]]:
    """
    Generate the full management report.
    - dry_run: use deterministic dry_run_report (no API); same 3 sections, labelled (Generated without AI — Dry Run).
    - output_mode "text": full report string from the model or from dry_run_report.
    - output_mode "json": dict with title, summary_bullets, reasons_bullets, todo_items, data_needed_next_month (or error string).
    """
    metrics = compute_metrics(inp)
    if dry_run:
        if output_mode == "json":
            return dry_run_report_json(inp, metrics)
        return dry_run_report(inp, metrics)
    result = call_model_report(inp, metrics, output_mode=output_mode)
    return result


if __name__ == "__main__":
    run_self_check()
    print("All self-checks passed.")
