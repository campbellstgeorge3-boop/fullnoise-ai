# -----------------------------------------------------------------------------
# utils.py — Validation, formatting, and helpers for the Boss Assistant.
# -----------------------------------------------------------------------------
"""Validation, AUD formatting, and input parsing. No I/O or API calls."""

from dataclasses import dataclass
from typing import Any, Dict, Optional


# -----------------------------------------------------------------------------
# Input model and validation
# -----------------------------------------------------------------------------

@dataclass(frozen=True)
class BossInput:
    """Validated input: five numbers for the management report."""
    revenue_this_month: float
    revenue_last_month: float
    budget_this_month: float
    jobs_this_month: int
    jobs_last_month: int


class ValidationError(ValueError):
    """Raised when input numbers fail validation."""


def validate_and_parse(
    revenue_this_month: float,
    revenue_last_month: float,
    budget_this_month: float,
    jobs_this_month: int,
    jobs_last_month: int,
) -> BossInput:
    """
    Validate all five inputs (non-negative) and return a BossInput.
    Raises ValidationError if any value is invalid.
    """
    if revenue_this_month < 0 or revenue_last_month < 0:
        raise ValidationError("Revenue values must be >= 0")
    if budget_this_month < 0:
        raise ValidationError("Budget must be >= 0")
    if jobs_this_month < 0 or jobs_last_month < 0:
        raise ValidationError("Job counts must be >= 0")
    return BossInput(
        revenue_this_month=float(revenue_this_month),
        revenue_last_month=float(revenue_last_month),
        budget_this_month=float(budget_this_month),
        jobs_this_month=int(jobs_this_month),
        jobs_last_month=int(jobs_last_month),
    )


def parse_from_dict(data: Dict[str, Any]) -> BossInput:
    """Build BossInput from a dict (e.g. JSON). Keys: revenue_this_month, etc."""
    def num(key: str, default: float = 0.0) -> float:
        v = data.get(key)
        if v is None:
            return default
        return float(v)

    def int_num(key: str, default: int = 0) -> int:
        v = data.get(key)
        if v is None:
            return default
        return int(float(v))

    return validate_and_parse(
        revenue_this_month=num("revenue_this_month"),
        revenue_last_month=num("revenue_last_month"),
        budget_this_month=num("budget_this_month"),
        jobs_this_month=int_num("jobs_this_month"),
        jobs_last_month=int_num("jobs_last_month"),
    )


# -----------------------------------------------------------------------------
# Formatting (AUD)
# -----------------------------------------------------------------------------

def format_aud(value: float) -> str:
    """Format a number as AUD, e.g. $185,000.00 AUD."""
    return f"${value:,.2f} AUD"


def format_aud_signed(value: float) -> str:
    """Format a signed dollar change, e.g. -$25,000.00 AUD or +$10,000.00 AUD."""
    if value >= 0:
        return f"+{format_aud(value)}"
    return f"-{format_aud(abs(value))}"
