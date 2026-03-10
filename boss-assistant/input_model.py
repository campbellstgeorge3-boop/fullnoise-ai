"""
Validated input for the Boss Assistant v1.
Five numbers: revenue_this_month, revenue_last_month, budget_this_month,
jobs_this_month, jobs_last_month. All validated; formatted in AUD.
Optional: company_name, outstanding_quotes_count, overdue_invoices_count, notes.
"""
from dataclasses import dataclass
from typing import Optional


class ValidationError(ValueError):
    """Raised when input numbers are invalid."""


@dataclass(frozen=True)
class BossInput:
    revenue_this_month: float
    revenue_last_month: float
    budget_this_month: float
    jobs_this_month: int
    jobs_last_month: int
    company_name: Optional[str] = None
    outstanding_quotes_count: Optional[int] = None
    overdue_invoices_count: Optional[int] = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.revenue_this_month < 0 or self.revenue_last_month < 0:
            raise ValidationError("Revenue values must be >= 0")
        if self.budget_this_month < 0:
            raise ValidationError("Budget must be >= 0")
        if self.jobs_this_month < 0 or self.jobs_last_month < 0:
            raise ValidationError("Job counts must be >= 0")
        if self.outstanding_quotes_count is not None and self.outstanding_quotes_count < 0:
            raise ValidationError("Outstanding quotes count must be >= 0")
        if self.overdue_invoices_count is not None and self.overdue_invoices_count < 0:
            raise ValidationError("Overdue invoices count must be >= 0")

    @classmethod
    def from_dict(cls, data: dict) -> "BossInput":
        """Build from a dict (e.g. JSON file). Keys can be snake_case or mixed."""
        def get(key: str, default: float = 0):
            v = data.get(key) or data.get(key.replace("_", " ")) or default
            return v if v is not None else default
        def get_opt(key: str, default=None):
            v = data.get(key) or data.get("optional", {}).get(key)
            return v if v is not None else default
        return cls(
            revenue_this_month=float(get("revenue_this_month")),
            revenue_last_month=float(get("revenue_last_month")),
            budget_this_month=float(get("budget_this_month")),
            jobs_this_month=int(get("jobs_this_month")),
            jobs_last_month=int(get("jobs_last_month")),
            company_name=(get_opt("company_name") or "").strip() or None,
            outstanding_quotes_count=int(get_opt("outstanding_quotes_count")) if get_opt("outstanding_quotes_count") is not None else None,
            overdue_invoices_count=int(get_opt("overdue_invoices_count")) if get_opt("overdue_invoices_count") is not None else None,
            notes=(get_opt("notes") or "").strip(),
        )

    @classmethod
    def from_args(
        cls,
        revenue_this: float,
        revenue_last: float,
        budget: float,
        jobs_this: int,
        jobs_last: int,
        company_name: Optional[str] = None,
        outstanding_quotes_count: Optional[int] = None,
        overdue_invoices_count: Optional[int] = None,
        notes: str = "",
    ) -> "BossInput":
        return cls(
            revenue_this_month=float(revenue_this),
            revenue_last_month=float(revenue_last),
            budget_this_month=float(budget),
            jobs_this_month=int(jobs_this),
            jobs_last_month=int(jobs_last),
            company_name=company_name.strip() if company_name else None,
            outstanding_quotes_count=outstanding_quotes_count,
            overdue_invoices_count=overdue_invoices_count,
            notes=(notes or "").strip(),
        )


def format_aud(value: float) -> str:
    """Format number as AUD (e.g. $185,000.00)."""
    return f"${value:,.2f} AUD"
