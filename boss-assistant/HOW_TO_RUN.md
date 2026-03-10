# How to run the Boss Assistant

Do this **once**, then use the commands below whenever you want a report.

---

## One-time setup (about 2 minutes)

**1. Open PowerShell** and go to the boss-assistant folder:

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
```

**2. Create and activate the virtual environment:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

(If you get an execution policy error, run once: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`, then activate again.)

**3. Install dependencies:**

```powershell
pip install -r requirements.txt
```

**4. Add your OpenAI key** so you get full reports (reasons + to-do list):

- Create a file named `.env` in the `boss-assistant` folder.
- Put one line in it (use your real key):

```
OPENAI_API_KEY=sk-your-key-here
```

---

## Run a report

**Always** be in the `boss-assistant` folder and have the venv activated (you should see `(.venv)` in the prompt). If you opened a new terminal, run:

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\Activate.ps1
```

### Option A — One-off report from a file

Use your own numbers in a JSON file (copy `data.example.json` to e.g. `myfigures.json` and edit), then:

```powershell
python run.py --file myfigures.json
```

Report is printed in the terminal. To save it to a file:

```powershell
python run.py --file myfigures.json > report.txt
```

Or use the example file to test:

```powershell
python run.py --file data.example.json
```

### Option B — Automated run (inbox or scheduled)

Uses the **newest** CSV/JSON in the `inbox` folder (or a single file if you set that in config). Good for running on a schedule with no typing.

**First time:** copy the config and add a file to the inbox:

```powershell
copy auto_config.example.json auto_config.json
```

Put a CSV or JSON with your numbers into the `inbox` folder (see `inbox/sample.csv` for CSV format). Then:

```powershell
python run_automated.py
```

The report is written to **`reports/report_YYYY-MM-DD_HH-MM.txt`** (no need to redirect).

To run it on a schedule (e.g. first Monday of the month), schedule **`Run_automated.bat`** in Windows Task Scheduler — see **docs/AUTOMATION.md**.

### Option C — Use 12 months of actual data (history CSV)

If you have **every month’s figures** for Vision (revenue, jobs, budget) in one file:

1. Create a CSV with a **header row** and **one row per month** (oldest month first), e.g.:

   ```csv
   month,revenue,jobs_completed,budget
   2024-01,180000,10,200000
   2024-02,192000,11,200000
   ...
   2024-12,185000,12,200000
   ```

2. Save it in the `boss-assistant` folder as e.g. **`vision_12months.csv`** (or use the example: `vision_12months.example.csv`).

3. Run:

   ```powershell
   python run_from_history.py --file vision_12months.csv
   ```

   The script uses the **last two rows** as “this month” vs “last month” and generates the report. Add **`--dry-run`** if you don’t want to call the API. Save to a file:

   ```powershell
   python run_from_history.py --file vision_12months.csv --out report.txt
   ```

When you add next month’s row to the CSV and run again, you automatically get the new “this month vs last month” report. No need to retype numbers.

---

## Quick reference

| What you want              | Command |
|----------------------------|--------|
| One report, numbers in a file | `python run.py --file data.example.json` |
| Report from 12 months CSV  | `python run_from_history.py --file vision_12months.csv` |
| Save that report to a file | `python run.py --file data.example.json > report.txt` |
| Use newest file in inbox   | `python run_automated.py` (report goes to `reports/`) |
| Test without API (no key)  | `python run.py --file data.example.json --dry-run` or add `--dry-run` to any command |

All commands assume you are inside `boss-assistant` with the venv activated.
