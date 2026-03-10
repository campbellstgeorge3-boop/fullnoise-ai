"""
Section 1: Performance Summary.
Bullet points with $ and % changes; numbers validated and formatted in AUD.
Plain text, easy to copy/paste.
"""
from typing import List

from input_model import format_aud
from analysis import PerformanceMetrics


def build_performance_summary(metrics: PerformanceMetrics, company_name: str | None = None) -> str:
    """Return the Performance Summary section as plain text with bullet points."""
    lines: List[str] = []
    if company_name:
        lines.append(f"Management report — {company_name}")
        lines.append("")
    lines.append("1) PERFORMANCE SUMMARY")
    lines.append("")
    lines.append(f"• Revenue this month: {format_aud(metrics.revenue_this)}")
    lines.append(f"• Revenue last month: {format_aud(metrics.revenue_last)}")
    rev_sign = "+" if metrics.revenue_change_dollars >= 0 else ""
    rev_str = format_aud(metrics.revenue_change_dollars) if metrics.revenue_change_dollars >= 0 else "-" + format_aud(abs(metrics.revenue_change_dollars))
    lines.append(f"• Revenue change: {rev_sign}{rev_str} ({rev_sign}{metrics.revenue_change_pct}%)")
    lines.append("")
    if metrics.budget > 0:
        lines.append(f"• Budget this month: {format_aud(metrics.budget)}")
        vs_sign = "+" if metrics.revenue_vs_budget_dollars >= 0 else ""
        vs_str = format_aud(metrics.revenue_vs_budget_dollars) if metrics.revenue_vs_budget_dollars >= 0 else "-" + format_aud(abs(metrics.revenue_vs_budget_dollars))
        lines.append(f"• Revenue vs budget: {vs_sign}{vs_str} ({vs_sign}{metrics.revenue_vs_budget_pct}%)")
        lines.append("")
    lines.append(f"• Jobs completed this month: {metrics.jobs_this}")
    lines.append(f"• Jobs completed last month: {metrics.jobs_last}")
    jobs_sign = "+" if metrics.jobs_change >= 0 else ""
    lines.append(f"• Jobs change: {jobs_sign}{metrics.jobs_change} ({jobs_sign}{metrics.jobs_change_pct}%)")
    lines.append("")
    if metrics.jobs_this > 0 and metrics.jobs_last > 0:
        lines.append(f"• Average job value this month: {format_aud(metrics.avg_job_value_this)}")
        lines.append(f"• Average job value last month: {format_aud(metrics.avg_job_value_last)}")
        avg_sign = "+" if metrics.avg_job_value_change_pct >= 0 else ""
        lines.append(f"• Average job value change: {avg_sign}{metrics.avg_job_value_change_pct}%")
        lines.append("")
    return "\n".join(lines)
