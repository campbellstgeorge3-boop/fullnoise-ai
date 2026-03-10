"""
Suggest likely reasons for performance changes.
Rule-based from the analysis; can be extended with LLM later.
"""
from typing import List

from analyser import Analysis
from metrics import BossAssistantInput


def suggest_reasons(inp: BossAssistantInput, analysis: Analysis) -> List[str]:
    """Return a short list of likely reasons for how performance changed."""
    reasons: List[str] = []
    rev_down = analysis.revenue_change < 0
    rev_up = analysis.revenue_change > 0
    jobs_down = analysis.jobs_change < 0
    jobs_up = analysis.jobs_change > 0
    avg_down = analysis.avg_job_value_change_pct < -2
    avg_up = analysis.avg_job_value_change_pct > 2

    if rev_down:
        if jobs_down and analysis.jobs_last > 0:
            reasons.append("Fewer jobs were completed this period compared to last.")
        if avg_down and analysis.avg_job_value_last > 0:
            reasons.append("Lower average job value — mix of work may have shifted to smaller or lower-margin jobs.")
        if jobs_down and (inp.notes and "weather" in inp.notes.lower() or "rain" in inp.notes.lower()):
            reasons.append("Weather or site delays may have pushed work out.")
        if jobs_down and (inp.notes and "staff" in inp.notes.lower() or "shortage" in inp.notes.lower()):
            reasons.append("Staffing or resourcing may have limited how many jobs could be completed.")
        if inp.outstanding_quotes_count and inp.outstanding_quotes_count > 5:
            reasons.append("A backlog of outstanding quotes suggests follow-up may be slow — work not yet converted.")
        if not reasons:
            reasons.append("Revenue is down; check whether fewer jobs, lower job values, or timing of invoicing explain it.")

    if rev_up:
        if jobs_up:
            reasons.append("More jobs were completed this period.")
        if avg_up:
            reasons.append("Higher average job value — more high-value work or better mix.")
        if not reasons:
            reasons.append("Revenue is up; likely from more jobs, higher job values, or both.")

    if analysis.revenue_vs_budget < 0 and analysis.budget > 0:
        reasons.append("Revenue is below budget for this period — pipeline or conversion may need attention.")

    return reasons[:6]
