"""
Assemble the full management report: 3 sections.
Section 1 from code; sections 2 and 3 from OpenAI or dry-run placeholder.
Plain text, easy to copy/paste.
"""
from input_model import BossInput
from analysis import compute
from performance_summary import build_performance_summary
from openai_sections import fetch_reasons_and_todos

DRY_RUN_REASONS = """2) LIKELY REASONS

• [Dry run] No API call. Run without --dry-run to generate ranked hypotheses from the inputs and construction context.
"""

DRY_RUN_TODOS = """3) BOSS TO-DO LIST

1. [Dry run] No API call. Run without --dry-run to generate 5 prioritized actions.
"""


def build_report(inp: BossInput, dry_run: bool = False) -> str:
    """
    Build the full report. If dry_run is True, sections 2 and 3 use placeholders.
    """
    metrics = compute(inp)
    section1 = build_performance_summary(metrics, company_name=inp.company_name)
    if dry_run:
        section2 = DRY_RUN_REASONS
        section3 = DRY_RUN_TODOS
    else:
        section2, section3 = fetch_reasons_and_todos(inp, metrics)
        if not section2.strip().upper().startswith("2)"):
            section2 = "2) LIKELY REASONS\n\n" + section2
        if not section3.strip().upper().startswith("3)"):
            section3 = "3) BOSS TO-DO LIST\n\n" + section3
    return section1 + "\n\n" + section2 + "\n\n" + section3
