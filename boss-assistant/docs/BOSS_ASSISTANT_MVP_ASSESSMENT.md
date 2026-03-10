# Boss Assistant — Senior engineer assessment and MVP plan

Assessment of the current `boss-assistant` repo: what it does, what exists, what's missing for a clean MVP, and a 3-step plan (no new features).

---

## 1) What the app does today

### Inputs

- **Core (always):** Five numbers — revenue this month, revenue last month, budget this month, jobs this month, jobs last month. Optional: company name, outstanding quotes count, overdue invoices count, notes.
- **Sources:**
  - **run.py:** CLI args, **JSON file only** (`--file`), or interactive prompts.
  - **run_automated.py:** Config-driven. One of: **file** (single JSON/CSV path), **inbox** (newest CSV/JSON in a folder), **api** (GET URL → JSON), **googledrive** (file or Sheet by ID), **myob** (OAuth + P&L API).
  - **run_from_history.py:** Single CSV with rows per month (columns: month, revenue, jobs_completed, budget); uses last two rows.

### Outputs

- **Single artifact:** A plain-text report in three sections:
  1. **Performance summary** — Revenue this/last, $ and % change, vs budget, jobs this/last, change, average job value and change (AUD).
  2. **Likely reasons** — Bullet list of hypotheses (from OpenAI, or placeholder in dry-run).
  3. **Boss to-do list** — Five numbered actions (from OpenAI, or placeholder in dry-run).
- **Where:** Printed to stdout (run.py, run_from_history.py) or written to `reports/report_YYYY-MM-DD_HH-MM.txt` (run_automated.py). Optional `--open` to open the file after write.

### Modes

| Mode | Entry point | Input | Output |
|------|-------------|--------|--------|
| Interactive | run.py (no args) | Prompts for 5 numbers | stdout |
| One-off from file | run.py --file &lt;path&gt; | JSON **only** (CSV not supported) | stdout |
| Dry-run | run.py --dry-run / run_automated (config dry_run) | Same as above | Same; sections 2 & 3 are placeholders |
| Automated | run_automated.py | Config: file / inbox / api / googledrive / myob | reports/ timestamped .txt |
| History CSV | run_from_history.py --file &lt;csv&gt; | Multi-row CSV (last 2 rows used) | stdout or --out file |

---

## 2) Files and their roles

### Core pipeline (used by run.py and run_automated.py)

| File | Role |
|------|------|
| **input_model.py** | BossInput dataclass, validation, from_dict/from_args, format_aud. |
| **analysis.py** | compute(BossInput) → PerformanceMetrics ($/% changes, avg job value). |
| **performance_summary.py** | Section 1 text from PerformanceMetrics (+ optional company_name). |
| **openai_sections.py** | fetch_reasons_and_todos(inp, metrics) → (reasons, todos) via OpenAI. |
| **report.py** | build_report(inp, dry_run) — assembles sections 1–3. |
| **run.py** | CLI: args / JSON file / interactive → BossInput → build_report → print. |
| **run_automated.py** | Load config → load input (file/inbox/api/googledrive/myob) → build_report → write to reports/. |
| **run_from_history.py** | CLI: history CSV → BossInput (last 2 rows) → build_report → print or --out. |

### Data loading (used by run_automated and/or run_from_history)

| File | Role |
|------|------|
| **data_loader.py** | load_from_json, load_from_csv, load_from_history_csv, get_latest_inbox_file, load_from_path, load_from_path_smart (CSV/JSON + history detection). |
| **api_loader.py** | load_from_api(url, headers, api_key_env) → BossInput. |
| **myob_loader.py** | Token refresh, P&L fetch, _sum_revenue_from_pl_response, load_from_myob_config. |
| **google_loader.py** | Drive service, download/export file or Sheet, load_from_googledrive_config. |

### Legacy / alternate (not used by run.py or run_automated.py)

| File | Role | Issue |
|------|------|--------|
| **main.py** | Alternate CLI (--text, --json, interactive); uses utils + boss_report. | Different entry and report shape; README still references main.py in places. |
| **boss_report.py** | Alternate metrics + OpenAI report (different PerformanceMetrics, prompts). | Duplicate of analysis + openai_sections + report. |
| **utils.py** | Alternate BossInput + validation + parse_from_dict (different module). | Duplicate of input_model. |
| **prompts.py** | System/user prompts for boss_report. | Duplicate of openai_sections prompts. |
| **metrics.py** | BossAssistantInput, PeriodMetrics (current/previous period + optional). | Different input model; not wired to any entry point. |
| **analyser.py** | analyse(BossAssistantInput) → Analysis (same idea as analysis.py). | Uses metrics.BossAssistantInput; dead code for current MVP. |
| **reasons.py** | Rule-based reasons from Analysis. | Uses analyser + metrics; dead for current MVP. |
| **todos.py** | Rule-based to-do list from Analysis. | Same. |
| **config.example.json** | Example for BossAssistantInput (current_period, previous_period, etc.). | Matches metrics/analyser stack, not run_automated. |

### Config and examples

| File | Role |
|------|------|
| **auto_config.json** | Runtime config (data_source, paths, company_name, dry_run, etc.); gitignored. |
| **auto_config.example.json** | Example for file/inbox. |
| **auto_config.api.example.json** | Example for data_source api. |
| **auto_config.myob.example.json** | Example for data_source myob. |
| **auto_config.googledrive.example.json** | Example for data_source googledrive. |
| **data.example.json** | Sample JSON input (5 numbers + optional fields). |
| **vision_12months.example.csv** | Sample history CSV (root and in vision_data). |
| **.env** / **.env.example** | OPENAI_API_KEY (and optional loader-specific keys); .env gitignored. |

### Docs and scripts

| File | Role |
|------|------|
| **README.md** | Setup and run; **still references main.py** and --text/--json in examples. |
| **HOW_TO_RUN.md** | run.py, run_automated, run_from_history; Option A/B/C. |
| **SEE_IT_RUN.md** | Minimal "see it run" steps (terminal + open report). |
| **docs/AUTOMATION.md** | Inbox, scheduling, data formats. |
| **docs/DATA_SOURCE_API.md** | API URL setup. |
| **docs/DATA_SOURCE_MYOB.md** | MYOB OAuth and config. |
| **docs/DATA_SOURCE_GOOGLEDRIVE.md** | Drive/Sheet and service account. |
| **Run_automated.bat** | Runs run_automated.py (venv + python). |
| **vision_data/** (README, VISION_SETUP, example CSV) | Inbox-style folder for Vision data. |
| **inbox/** (README, sample.csv) | Alternative inbox folder. |

### Dependencies

| File | Role |
|------|------|
| **requirements.txt** | openai, python-dotenv; optional google-auth, google-api-python-client for Drive. |

---

## 3) What is missing for a clean MVP (bugs, gaps, rough edges)

### Bugs / incorrect behaviour

- **run.py --file** only reads **JSON**. Passing a CSV (e.g. `run.py --file data.csv`) will fail with JSON decode error. Docs and HOW_TO_RUN imply "file" can be used for "one-off report"; CSV is supported in run_automated but not here.
- **company_name.strip()** in input_model.from_args: if `company_name` is None, calling `.strip()` would raise. Code uses `company_name.strip() if company_name else None`, so this is safe.

### Gaps

- **Single documented entry point:** README and some docs still say "main.py" and "--text"/"--json". The real primary entry points are run.py (interactive/one-off) and run_automated.py (scheduled/all sources). So "how to run" is split and partly wrong.
- **Optional dependencies:** Google (and MYOB) loaders are optional. If someone sets data_source to googledrive/myob without installing the deps, they get a runtime ImportError. No clear "optional extras" or check on startup.
- **.env.example:** Referenced in README; if missing, "copy .env.example .env" fails. (Assessment found .env.example exists; ensure it's committed and README matches.)

### Rough edges / duplication

- **Two CLIs:** run.py (input_model + report) and main.py (utils + boss_report) do similar things with different types and outputs. New users don't know which to run; README points to main.py.
- **Two input models:** BossInput (input_model) vs BossAssistantInput (metrics). Only BossInput is used by the live pipeline. metrics/analyser/reasons/todos/config.example.json form an unused stack.
- **Multiple "how to run" docs:** README, HOW_TO_RUN, SEE_IT_RUN, AUTOMATION, plus per–data-source docs. Overlap and some inconsistency (e.g. main.py vs run.py).
- **Four auto_config examples:** file/inbox, api, myob, googledrive. Good for flexibility, but there is no single "start here" default that matches the README (e.g. "run with data.example.json").
- **run_from_history.py** is a separate script; its behaviour (history CSV → last 2 rows) is also available via data_loader.load_from_path_smart when a CSV has a "month" column and 2+ rows. So "history" is supported in two ways (script vs inbox/file CSV).

### Not blocking MVP but worth noting

- No tests.
- No explicit validation of config (e.g. unknown data_source, missing keys for myob/googledrive) beyond runtime errors.
- os.startfile in run_automated is Windows-only; harmless on other OS but "open report" won't work there.

---

## 4) Three-step plan (smallest set of changes first; no new features)

### Step 1 — One entry point and one "run" story (docs + CSV for run.py)

**Goal:** A single, clear "how to run" story and fix the run.py CSV gap.

- **1.1** **README.md:** Make run.py the primary CLI. Replace all main.py references with run.py. Remove or reword --text/--json (run.py only does plain-text report). Keep "dry-run" and "from file" and "run_automated" as the two ways to run.
- **1.2** **run.py --file:** Support CSV as well as JSON. If path has `.csv` or content looks like CSV, use data_loader.load_from_path_smart on that path (or a small helper that builds BossInput from CSV); if JSON, keep current behaviour. This aligns run.py with run_automated's file behaviour.
- **1.3** **HOW_TO_RUN.md:** Shorten and align with README: "One-off = run.py (interactive or --file). Automated = run_automated.py + auto_config." Optionally point "first run" at run.py --file data.example.json --dry-run.

**Outcome:** New users follow README, use run.py for one-off and run_automated for scheduled; run.py --file works for both JSON and CSV. No new features.

---

### Step 2 — Remove or isolate legacy code (reduce confusion)

**Goal:** One pipeline only; no duplicate entry points or input models for MVP.

- **2.1** **Decide:** Either delete or move to a `_legacy/` (or `_archive/`) folder: main.py, boss_report.py, utils.py, prompts.py, config.example.json. Same for the "metrics + analyser + reasons + todos" stack: metrics.py, analyser.py, reasons.py, todos.py — either remove or archive. Recommendation: archive (move to `_legacy/`) so nothing breaks if something still references them; then delete once confirmed unused.
- **2.2** **README / docs:** Remove any remaining references to main.py, boss_report, utils, prompts, config.example (for the old BossAssistantInput). List the single pipeline: input_model → analysis → performance_summary + openai_sections → report; entry points run.py and run_automated.py.

**Outcome:** Only one input model (BossInput), one report path (report.build_report), and two entry points (run.py, run_automated.py). Clear what to run and what to ignore.

---

### Step 3 — Config and docs cleanup (one example, optional deps)

**Goal:** One obvious config starting point; clear errors when optional loaders are used but not installed.

- **3.1** **auto_config.example.json:** Keep as the single "copy this to auto_config.json" template. Ensure it has data_source "file", data_file "data.json", output_dir "reports", and optional company_name. Add a one-line comment (in a separate README or in docs) that other data sources (inbox, api, googledrive, myob) have their own example files and docs.
- **3.2** **run_automated.py:** When data_source is googledrive or myob, catch ImportError from the loader and print a clear message (e.g. "Install optional deps: pip install google-auth google-api-python-client" or "MYOB loader has no extra deps; check MYOB_* env vars"). No new features, just better errors.
- **3.3** **docs:** Add a single "BOSS_ASSISTANT_QUICKSTART.md" (or a short section in README) that says: (1) venv + pip install -r requirements.txt, (2) .env with OPENAI_API_KEY, (3) run.py --file data.example.json (or run_automated with data_source file and data_file data.json). Link to HOW_TO_RUN and AUTOMATION for details. Optionally trim SEE_IT_RUN into that page or into HOW_TO_RUN so there aren't three "how to run" docs.

**Outcome:** One default config example, clear path to first run, and clear errors for optional data sources. No new behaviour.

---

## Summary

| # | Focus | Deliverable |
|---|--------|-------------|
| 1 | One run story + CSV for run.py | README and HOW_TO_RUN point to run.py; run.py --file supports CSV; first-run = run.py --file data.example.json. |
| 2 | Single pipeline | Legacy main/boss_report/utils/prompts and metrics/analyser/reasons/todos archived or removed; docs list only run.py + run_automated.py and input_model → report. |
| 3 | Config and optional deps | One auto_config.example (file-based); friendly ImportError for googledrive/myob; one short quickstart. |

No new features; only fixes, removal of duplication, and clearer docs and config for a clean MVP "Boss Assistant."
