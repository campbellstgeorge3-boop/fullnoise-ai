# How to Build the AI Boss Assistant for Vision Constructions

A practical blueprint: what exists, how it fits together, and how to grow it into an Actualisation-style management and operations system.

---

## 1. What You Asked For (and What You Have)

**Goal:** A smart business analyst and planning coach that:

- Takes **simple numbers** each month (or week): this month’s revenue, last month’s revenue, budget, jobs completed this period vs last.
- Produces a **plain-English management report** that explains:
  - Whether performance is up or down and how it compares to budget.
  - What has changed (revenue, jobs, average job value).
- **Analyses likely reasons** (e.g. fewer jobs, lower average job value, weather/staffing delays, slow quote follow-up, lack of high-value work in the pipeline).
- Ends with a **prioritised boss to-do list** (e.g. follow up quotes, pre-book work, fix bottlenecks, focus on higher-value jobs, chase overdue invoices).

**Current state:** You already have a **working v1** in `boss-assistant/` that does exactly this:

| Piece | Where | What it does |
|-------|--------|---------------|
| Input | `input_model.py`, `run.py` | 5 numbers: revenue this/last, budget, jobs this/last. CLI, JSON file, or interactive. |
| Metrics | `analysis.py` | Computes $ and % changes, revenue vs budget, average job value and its change. |
| Section 1 | `performance_summary.py` | Bullet-point performance summary in plain English (AUD). |
| Sections 2 & 3 | `openai_sections.py` | Calls OpenAI to generate **Likely Reasons** and **Boss To-Do List** from the numbers + construction context (no invented facts). |
| Report | `report.py` | Assembles all three sections; supports `--dry-run` (no API) for testing. |

So the “how would you build this?” answer for the **first version** is: **you’ve already built it.** The next step is to **use it at Vision Constructions**, then extend it as below.

---

## 2. Architecture: How It’s Built (and How to Extend It)

### 2.1 Core flow (current)

```
User input (5 numbers)
    → BossInput (validated)
    → compute(PerformanceMetrics)
    → Section 1: build_performance_summary (deterministic)
    → Section 2 & 3: fetch_reasons_and_todos (OpenAI, construction context)
    → Full report (plain text)
```

- **Section 1** is 100% from your numbers (no AI).
- **Sections 2 & 3** use one OpenAI call with a single prompt that includes:
  - The 5 inputs and all computed metrics (revenue change, vs budget, jobs change, average job value change).
  - Instructions to only use that data + general construction knowledge (weather, labour, quoting, scheduling, invoicing, pipeline).
  - Format: “2) LIKELY REASONS” with bullets, “3) BOSS TO-DO LIST” with 5 numbered actions.

This keeps the system simple, auditable, and easy to test with `--dry-run`.

### 2.2 Optional rich input (already in the codebase)

There is a **second input model** in `metrics.py` (`BossAssistantInput`) that supports:

- **Company name** (e.g. “Vision Constructions”).
- **Period type**: month or week.
- **Optional**: outstanding quotes count, overdue invoices count, free-text notes.

`analyser.py`, `reasons.py`, and `todos.py` use this model and produce **rule-based** reasons and to-dos (e.g. “Follow up outstanding quotes” when `outstanding_quotes_count > 0`). This pipeline is **not** currently wired into `run.py`. Unifying it gives you:

- One entry point that accepts either the simple 5 numbers or the richer JSON.
- Option to use **rules** when you have quotes/invoices data, and **LLM** to add nuance or when you only have the 5 numbers.

### 2.3 How to grow it (Actualisation-style)

Think of the Boss Assistant as the **first agent** in a larger “AI Factory” for Vision Constructions:

1. **Data layer (now)**  
   - Input = a few numbers (and optionally quotes/invoices/notes).  
   - Later: same report can be fed from a **single source of truth** (spreadsheet export, Xero/Jobpac API, or a small DB).

2. **More inputs (next)**  
   - Add fields when they’re easy to get: quotes sent this month, conversion rate, overdue invoices $, pipeline value, job types.  
   - Keep the same report structure; the LLM and/or rules just get more context.

3. **More outputs (next)**  
   - Same report could drive: weekly email digest, PDF for the board, or a simple dashboard (e.g. Next.js page that calls the same `build_report` logic).

4. **Automation**  
   - Monthly/weekly job that pulls numbers from a file or API and runs the assistant, then emails or posts the report (e.g. to Slack/Teams).

5. **More agents**  
   - **Scheduling / resourcing agent** (e.g. “who’s on what job next week”) using the same data layer.  
   - **Quote follow-up agent** (remind to chase quotes, suggest which to prioritise).  
   - **Cash-flow agent** (invoices, payments, forecasts).  

The Boss Assistant stays the **“boss view”**: one report that answers “how are we doing and what should I do next?”. Other agents can feed it data or act on its to-do list.

---

## 3. Concrete Next Steps

### 3.1 Use it at Vision Constructions today

1. **Setup** (see `boss-assistant/README.md`):  
   - Python 3.10+, venv, `pip install -r requirements.txt`, set `OPENAI_API_KEY` (or use `--dry-run` to test without it).

2. **Run with real numbers** (example):  
   ```powershell
   cd boss-assistant
   python run.py --revenue-this 185000 --revenue-last 210000 --budget 200000 --jobs-this 12 --jobs-last 14
   ```  
   Or put the same numbers in a JSON file and run:  
   `python run.py --file data.json`

3. **Share the report**: Copy the plain-text output into email or a doc; optionally redirect to a file:  
   `python run.py --file data.json > report.txt`

### 3.2 Optional: add Vision Constructions branding and rich input

- Add a **company name** (e.g. “Vision Constructions”) to the report header so the output is clearly for that business.
- Support **optional** fields in the JSON (e.g. `outstanding_quotes_count`, `overdue_invoices_count`, `notes`) and pass them into the OpenAI prompt so reasons and to-dos can reference them (e.g. “You have 8 outstanding quotes — follow up to convert to booked work”).
- Optionally wire in the existing **rule-based** reasons and to-dos when those optional fields are present, and use the LLM to **add** or **refine** items rather than replace them.

### 3.3 Later: make it the first block of your “Actualisation-style” business

- **Single source of truth**: Replace manual JSON entry with a monthly export (CSV/Excel) or an API (Xero, Aroflo, etc.) and a small script that maps that data into `BossInput` (or `BossAssistantInput`) and runs the assistant.
- **Scheduling**: Run the assistant on a schedule (e.g. first Monday of the month) and email or post the report.
- **Productise**: Offer the same report (and later, more agents) to other construction/trade businesses as a paid “management cockpit” — same architecture, different company name and data source.

---

## 4. Summary

- **Build v1:** You already have it: 5 numbers in → performance summary + likely reasons + boss to-do list. Use it at Vision Constructions with real numbers.
- **Extend v1:** Add company name and optional quotes/invoices/notes; optionally unify with the rule-based pipeline for richer, data-driven reasons and to-dos.
- **Grow:** Treat the Boss Assistant as the first agent on a shared data layer; add more inputs, more outputs, automation, and more agents (scheduling, quotes, cash flow) so it becomes the core of an Actualisation-style AI business for construction.

All of this can start as the simple, easy-to-use tool you run inside Vision Constructions and grow step by step without a big rewrite.
