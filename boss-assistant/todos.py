"""
Generate a prioritised boss to-do list from the analysis and optional data.
Actions are practical: follow up quotes, pre-book work, fix bottlenecks, etc.
"""
from dataclasses import dataclass
from typing import List

from analyser import Analysis
from metrics import BossAssistantInput


@dataclass
class TodoItem:
    priority: int  # 1 = highest
    action: str
    reason: str


def generate_todos(inp: BossAssistantInput, analysis: Analysis) -> List[TodoItem]:
    """Build a short, prioritised list of actions for the boss."""
    todos: List[TodoItem] = []
    rev_below_budget = analysis.budget > 0 and analysis.revenue_this < analysis.budget
    rev_down = analysis.revenue_change < 0
    jobs_down = analysis.jobs_change < 0

    # Outstanding quotes → follow up
    if inp.outstanding_quotes_count and inp.outstanding_quotes_count > 0:
        todos.append(TodoItem(
            priority=1,
            action="Follow up outstanding quotes to convert them to booked work.",
            reason=f"You have {inp.outstanding_quotes_count} quote(s) outstanding.",
        ))

    # Overdue invoices → chase
    if inp.overdue_invoices_count and inp.overdue_invoices_count > 0:
        todos.append(TodoItem(
            priority=2,
            action="Chase overdue invoices to improve cash flow.",
            reason=f"{inp.overdue_invoices_count} overdue invoice(s) on the books.",
        ))

    # Below budget
    if rev_below_budget:
        todos.append(TodoItem(
            priority=3 if todos else 1,
            action="Focus on filling the pipeline: pre-book work and lock in start dates.",
            reason="Revenue is below budget this period.",
        ))

    # Revenue down → bottlenecks / delays
    if rev_down and jobs_down:
        todos.append(TodoItem(
            priority=4,
            action="Identify and fix bottlenecks that caused delays (resourcing, materials, or scheduling).",
            reason="Fewer jobs completed than last period.",
        ))

    # Low average job value
    if analysis.avg_job_value_change_pct < -5 and analysis.avg_job_value_last > 0:
        todos.append(TodoItem(
            priority=5,
            action="Shift sales and quoting toward higher-value jobs where possible.",
            reason="Average job value is down — mix may be skewed to smaller work.",
        ))

    # Pipeline / quotes if revenue down and we haven't already said it
    if rev_down and not any("quote" in t.action.lower() for t in todos):
        todos.append(TodoItem(
            priority=6,
            action="Follow up outstanding quotes and push to pre-book work for next period.",
            reason="Revenue dropped; converting quotes and locking in work will help.",
        ))

    # Sort by priority and cap at 6
    todos.sort(key=lambda t: t.priority)
    return todos[:6]
