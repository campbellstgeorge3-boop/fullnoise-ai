"""
Analyse period-over-period and vs budget.
Produces structured results for the report and to-do logic.
"""
from dataclasses import dataclass
from metrics import BossAssistantInput, PeriodMetrics


@dataclass
class Analysis:
    """Results of the analysis."""
    # Revenue
    revenue_this: float
    revenue_last: float
    revenue_change: float
    revenue_change_pct: float
    revenue_vs_budget: float
    revenue_vs_budget_pct: float
    # Jobs
    jobs_this: int
    jobs_last: int
    jobs_change: int
    jobs_change_pct: float
    # Derived
    avg_job_value_this: float
    avg_job_value_last: float
    avg_job_value_change_pct: float
    # Budget
    budget: float
    period_label: str  # "month" or "week"


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(100 * (current - previous) / previous, 1)


def _avg_job(revenue: float, jobs: int) -> float:
    if jobs <= 0:
        return 0.0
    return round(revenue / jobs, 2)


def analyse(inp: BossAssistantInput) -> Analysis:
    """Compute all metrics and comparisons."""
    cur = inp.current_period
    prev = inp.previous_period
    budget = inp.budget

    rev_change = cur.revenue - prev.revenue
    rev_change_pct = _pct_change(cur.revenue, prev.revenue)
    rev_vs_budget = cur.revenue - budget if budget else 0
    rev_vs_budget_pct = _pct_change(cur.revenue, budget) if budget else 0.0

    jobs_change = cur.jobs_completed - prev.jobs_completed
    jobs_change_pct = _pct_change(float(cur.jobs_completed), float(prev.jobs_completed))

    avg_this = _avg_job(cur.revenue, cur.jobs_completed)
    avg_last = _avg_job(prev.revenue, prev.jobs_completed)
    avg_change_pct = _pct_change(avg_this, avg_last) if avg_last else 0.0

    return Analysis(
        revenue_this=cur.revenue,
        revenue_last=prev.revenue,
        revenue_change=round(rev_change, 2),
        revenue_change_pct=rev_change_pct,
        revenue_vs_budget=round(rev_vs_budget, 2),
        revenue_vs_budget_pct=rev_vs_budget_pct,
        jobs_this=cur.jobs_completed,
        jobs_last=prev.jobs_completed,
        jobs_change=jobs_change,
        jobs_change_pct=jobs_change_pct,
        avg_job_value_this=avg_this,
        avg_job_value_last=avg_last,
        avg_job_value_change_pct=avg_change_pct,
        budget=budget,
        period_label="month" if inp.period_type == "month" else "week",
    )
