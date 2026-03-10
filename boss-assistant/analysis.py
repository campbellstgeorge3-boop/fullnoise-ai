"""
Compute performance metrics from the 5 inputs.
All $ and % changes for the report; no LLM.
"""
from dataclasses import dataclass

from input_model import BossInput


@dataclass
class PerformanceMetrics:
    """Computed values for the performance summary."""
    revenue_this: float
    revenue_last: float
    revenue_change_dollars: float
    revenue_change_pct: float
    revenue_vs_budget_dollars: float
    revenue_vs_budget_pct: float
    jobs_this: int
    jobs_last: int
    jobs_change: int
    jobs_change_pct: float
    avg_job_value_this: float
    avg_job_value_last: float
    avg_job_value_change_pct: float
    budget: float


def _pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(100 * (current - previous) / previous, 1)


def _avg_job(revenue: float, jobs: int) -> float:
    if jobs <= 0:
        return 0.0
    return round(revenue / jobs, 2)


def compute(inp: BossInput) -> PerformanceMetrics:
    """Compute all performance metrics from the 5 inputs."""
    rev_this = inp.revenue_this_month
    rev_last = inp.revenue_last_month
    budget = inp.budget_this_month
    jobs_this = inp.jobs_this_month
    jobs_last = inp.jobs_last_month

    rev_change = round(rev_this - rev_last, 2)
    rev_pct = _pct_change(rev_this, rev_last)
    vs_budget = round(rev_this - budget, 2) if budget else 0.0
    vs_budget_pct = _pct_change(rev_this, budget) if budget else 0.0

    jobs_change = jobs_this - jobs_last
    jobs_pct = _pct_change(float(jobs_this), float(jobs_last))

    avg_this = _avg_job(rev_this, jobs_this)
    avg_last = _avg_job(rev_last, jobs_last)
    avg_pct = _pct_change(avg_this, avg_last) if avg_last else 0.0

    return PerformanceMetrics(
        revenue_this=rev_this,
        revenue_last=rev_last,
        revenue_change_dollars=rev_change,
        revenue_change_pct=rev_pct,
        revenue_vs_budget_dollars=vs_budget,
        revenue_vs_budget_pct=vs_budget_pct,
        jobs_this=jobs_this,
        jobs_last=jobs_last,
        jobs_change=jobs_change,
        jobs_change_pct=jobs_pct,
        avg_job_value_this=avg_this,
        avg_job_value_last=avg_last,
        avg_job_value_change_pct=avg_pct,
        budget=budget,
    )
