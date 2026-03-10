# AI Boss Assistant v1 (Vision Constructions)

CLI tool: input **5 numbers** (revenue this/last month, budget, jobs this/last month). Optional: company name, outstanding quotes count, overdue invoices count, notes.  
**Output:** 3-section plain-text report (Performance Summary, Likely Reasons, Boss To-Do List). Uses OpenAI for reasons and to-dos.

## Project layout

```
boss-assistant/
  run.py                 # CLI entry
  input_model.py         # Validated input (5 numbers + optional fields)
  analysis.py            # Compute $ and % changes
  performance_summary.py # Section 1 (bullets)
  openai_sections.py     # Sections 2 & 3 (OpenAI API)
  report.py              # Assemble full report; dry_run support
  requirements.txt
  README.md
  data.example.json      # Example input (Vision Constructions)
  .env                   # Optional; OPENAI_API_KEY (do not commit)
```

## Setup (Windows)

1. **Python 3.10+** (e.g. `python --version`).

2. **Virtual environment (recommended):**
   ```powershell
   cd boss-assistant
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   If you get an execution policy error:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **OpenAI API key:** Set `OPENAI_API_KEY` (not needed for `--dry-run`).  
   **Option A** — current session: `$env:OPENAI_API_KEY = "sk-your-key-here"`  
   **Option B** — create `boss-assistant\.env`: `OPENAI_API_KEY=sk-your-key-here`  
   The app loads `.env` via python-dotenv. Do not commit `.env`.

## Run

From the `boss-assistant` folder with the venv activated:

**Dry-run (no API call):**
```powershell
python run.py --dry-run
python run.py --file data.example.json --dry-run
python run.py --revenue-this 185000 --revenue-last 210000 --budget 200000 --jobs-this 12 --jobs-last 14 --dry-run
```

**Full report (uses OpenAI):**
```powershell
python run.py
python run.py --file data.example.json
python run.py --revenue-this 185000 --revenue-last 210000 --budget 200000 --jobs-this 12 --jobs-last 14
```

**With optional context (company name, quotes, invoices, notes):**
```powershell
python run.py --file data.example.json
python run.py --revenue-this 185000 --revenue-last 210000 --budget 200000 --jobs-this 12 --jobs-last 14 --company "Vision Constructions" --quotes 8 --invoices 3 --notes "Wet month; two jobs delayed."
```

**Output to file:**
```powershell
python run.py --file data.example.json > report.txt
```

## JSON file format

**Required:** `revenue_this_month`, `revenue_last_month`, `budget_this_month`, `jobs_this_month`, `jobs_last_month`

**Optional:** `company_name`, `outstanding_quotes_count`, `overdue_invoices_count`, `notes`

See `data.example.json` for a full example (Vision Constructions with optional fields).

## Validation and formatting

- All numbers must be **>= 0**.
- Money is formatted in **AUD** (e.g. `$185,000.00 AUD`).
- Invalid input produces a clear error and exit code 1.
