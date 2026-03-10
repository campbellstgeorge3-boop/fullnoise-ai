"""
Input metrics for the Boss Assistant.
Simple numbers each month/week: revenue, budget, jobs completed.
Optional fields for future growth (quotes, invoices, notes).
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PeriodMetrics:
    """One period (month or week)."""
    revenue: float
    jobs_completed: int


@dataclass
class BossAssistantInput:
    """All inputs for one run."""
    company_name: str
    period_type: str  # "month" or "week"
    currency: str
    current_period: PeriodMetrics
    previous_period: PeriodMetrics
    budget: float
    # Optional for future expansion
    outstanding_quotes_count: Optional[int] = None
    overdue_invoices_count: Optional[int] = None
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> "BossAssistantInput":
        cur = data.get("current_period", {})
        prev = data.get("previous_period", {})
        opt = data.get("optional", {})
        return cls(
            company_name=data.get("company_name", "My Business"),
            period_type=data.get("period_type", "month"),
            currency=data.get("currency", "AUD"),
            current_period=PeriodMetrics(
                revenue=float(cur.get("revenue", 0)),
                jobs_completed=int(cur.get("jobs_completed", 0)),
            ),
            previous_period=PeriodMetrics(
                revenue=float(prev.get("revenue", 0)),
                jobs_completed=int(prev.get("jobs_completed", 0)),
            ),
            budget=float(data.get("budget", 0)),
            outstanding_quotes_count=opt.get("outstanding_quotes_count"),
            overdue_invoices_count=opt.get("overdue_invoices_count"),
            notes=(opt.get("notes") or "").strip(),
        )
