# -----------------------------------------------------------------------------
# prompts.py — System and user prompt templates for the Boss Assistant.
# -----------------------------------------------------------------------------
"""Prompt templates for the OpenAI model. Placeholders are filled by boss_report."""

# -----------------------------------------------------------------------------
# System prompt (fixed)
# -----------------------------------------------------------------------------

SYSTEM_PROMPT = """You are a construction business performance analyst for Australia. All figures are in AUD. You are conservative: base your analysis only on the data provided and general construction industry context. Do not hallucinate facts, numbers, or causes. If something is uncertain, frame it as a possible hypothesis, not a certainty. Output only the requested format—no preamble or commentary."""


# -----------------------------------------------------------------------------
# User prompt template (plain-text report)
# Placeholder: {context_block} is replaced with inputs + computed metrics.
# -----------------------------------------------------------------------------

USER_PROMPT_TEMPLATE = """Using only the data below, write a monthly performance report. Follow the formatting requirements exactly.

{context_block}

---

Formatting requirements (use these exact headers and structure):

**Title line (first line):**
Vision Constructions — Monthly Performance Report

**1) Performance Summary**
- 4 to 7 bullet points.
- Each bullet must reference at least one number from the data (e.g. revenue, %, jobs, budget gap).
- Use the exact header: 1) Performance Summary

**2) Likely Reasons (Hypotheses)**
- 3 to 6 bullet points, ranked from most likely to least likely.
- Use language like "possible", "may", "could" — avoid certainty (do not say "this is because" or "the reason is").
- Use the exact header: 2) Likely Reasons (Hypotheses)

**3) Boss To-Do List (Next 30 Days)**
- Exactly 5 numbered actions (1. … 2. … 3. … 4. … 5.).
- Each action must start with a verb (e.g. Call, Review, Schedule, Follow up, Chase).
- Each action must include a short reason in parentheses at the end of the same line.
- Use the exact header: 3) Boss To-Do List (Next 30 Days)

**End with one line:**
Data Needed Next Month: [one short suggestion for what data or metric to add or track next month]

Output plain text only. No markdown headings beyond the headers above. No extra commentary before or after the report."""


# -----------------------------------------------------------------------------
# User prompt template — JSON mode variant
# Same context_block; model returns structured JSON.
# -----------------------------------------------------------------------------

USER_PROMPT_JSON_TEMPLATE = """Using only the data below, produce a monthly performance report as structured JSON. Do not invent numbers or facts.

{context_block}

---

Return a single JSON object with exactly these fields:

- **title** (string): "Vision Constructions — Monthly Performance Report"
- **summary_bullets** (array of strings): 4 to 7 bullets for the performance summary. Each bullet must reference at least one number from the data.
- **reasons_bullets** (array of strings): 3 to 6 bullets for likely reasons, ranked most likely first. Use "possible" / "may" / "could" — avoid certainty language.
- **todo_items** (array of strings): Exactly 5 items. Each must start with a verb (e.g. Call, Review, Schedule) and include a reason in parentheses. Example: "Follow up outstanding quotes (to convert pipeline to revenue)."
- **data_needed_next_month** (string): One short line suggesting what data or metric to add or track next month.

Example shape (do not include comments):
{
  "title": "Vision Constructions — Monthly Performance Report",
  "summary_bullets": ["Revenue this month was $X AUD (...).", "..."],
  "reasons_bullets": ["Possible cause: ...", "..."],
  "todo_items": ["Call key clients to confirm start dates (lock in pipeline).", "..."],
  "data_needed_next_month": "Track outstanding quote values to forecast next month revenue."
}

Output only valid JSON. No markdown code fences, no explanation before or after."""


# -----------------------------------------------------------------------------
# User prompt — sections 2 & 3 only (use when section 1 is built in code)
# Same formatting rules for 2 and 3; includes "Data Needed Next Month" at end.
# -----------------------------------------------------------------------------

USER_PROMPT_SECTIONS_2_3_TEMPLATE = """Using only the data below, write sections 2 and 3 of the monthly performance report plus the closing line. Follow the formatting requirements exactly.

{context_block}

---

Output plain text only. Use these exact headers and structure:

**2) Likely Reasons (Hypotheses)**
- 3 to 6 bullet points, ranked most likely first.
- Use "possible", "may", "could" — avoid certainty language.
- Use the exact header: 2) Likely Reasons (Hypotheses)

**3) Boss To-Do List (Next 30 Days)**
- Exactly 5 numbered actions (1. … 2. … 3. … 4. … 5.).
- Each action starts with a verb (e.g. Call, Review, Schedule) and includes a reason in parentheses.
- Use the exact header: 3) Boss To-Do List (Next 30 Days)

**End with one line:**
Data Needed Next Month: [one short suggestion]

No preamble. No section 1 (it is generated separately)."""
