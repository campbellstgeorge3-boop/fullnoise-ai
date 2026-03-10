# Running the Boss Assistant by itself (no manual data entry)

The report can run on a schedule and **use the latest file you drop or export** — no need to open the app or type numbers in.

1. **One-time setup** — config + inbox folder
2. **Each period** — save or export a CSV/JSON into the inbox (or have your system save it there)
3. **Schedule** — Task Scheduler runs the report; it uses the newest file in the inbox and writes the report to `reports/`

---

## 1. One-time setup

### 1.1 Use the inbox (recommended — no typing)

Set the automation config to read from the **inbox** folder. The run will use the **newest** `.json` or `.csv` file in that folder (by modification time).

```powershell
cd boss-assistant
copy auto_config.example.json auto_config.json
```

Edit `auto_config.json` and set:

```json
{
  "data_source": "inbox",
  "inbox_dir": "inbox",
  "output_dir": "reports",
  "dry_run": false
}
```

- **`data_source`: `"inbox"`** — use the newest file in `inbox_dir`. No need to edit a single “data file” by hand.
- **`inbox_dir`** — folder path (relative to boss-assistant). Default `"inbox"` (the `boss-assistant/inbox` folder).
- **`output_dir`** — where timestamped reports are written (e.g. `reports`).

**How you get data into the inbox (no manual entry):**

- **Export from Excel:** Save your sheet as CSV with the right columns (see below) and save/copy it into `boss-assistant/inbox/`. Overwrite the same file each month (e.g. `monthly_figures.csv`) or add new files — the run always uses the **newest** file.
- **Export from Xero / your system:** If your software can export to a folder, point it at the inbox folder (or a shared path that you sync/copy into inbox). Same idea: newest file wins.
- **Network/Dropbox:** You can set `inbox_dir` to a full path (e.g. `C:\Dropbox\VisionConstructions\boss_inbox`) so the bookkeeper saves the export there; the scheduled task reads from that folder.

So: **you only “put” a file in place (save/export/copy). The rest runs by itself.**

### 1.2 File formats in the inbox

**CSV (with header)** — one header row, one data row. Column names (order optional if you use headers):

- `revenue_this_month`, `revenue_last_month`, `budget_this_month`, `jobs_this_month`, `jobs_last_month`
- Optional: `company_name`, `outstanding_quotes_count`, `overdue_invoices_count`, `notes`

Example (see `inbox/sample.csv`):

```csv
revenue_this_month,revenue_last_month,budget_this_month,jobs_this_month,jobs_last_month,company_name,outstanding_quotes_count,overdue_invoices_count,notes
185000,210000,200000,12,14,Vision Constructions,8,3,Wet month; two jobs delayed.
```

**CSV (no header)** — single row of numbers in this order:  
revenue_this_month, revenue_last_month, budget_this_month, jobs_this_month, jobs_last_month  
Optional extra columns: company_name, outstanding_quotes_count, overdue_invoices_count, notes.

**JSON** — same keys as `data.example.json`:  
`revenue_this_month`, `revenue_last_month`, `budget_this_month`, `jobs_this_month`, `jobs_last_month`, and optionally `company_name`, `outstanding_quotes_count`, `overdue_invoices_count`, `notes`.

### 1.3 Alternative: single data file (manual edit)

If you prefer to edit one file by hand instead of using the inbox:

In `auto_config.json` set:

```json
{
  "data_source": "file",
  "data_file": "data.json",
  "output_dir": "reports",
  "dry_run": false
}
```

Then create/update `data.json` each period (copy from `data.example.json` and edit). The run will use that file. CSV is also supported for `data_file` (e.g. `"data_file": "data.csv"`).

### 1.4 Config reference

| Key           | Meaning |
|---------------|--------|
| `data_source`| `"inbox"` = use newest file in `inbox_dir`. `"file"` = use `data_file` path. |
| `inbox_dir`  | Folder to look in when `data_source` is `"inbox"`. Relative or absolute path. |
| `data_file`  | Path to one file when `data_source` is `"file"`. JSON or CSV. |
| `output_dir` | Where report files are written (e.g. `reports`). |
| `dry_run`    | `true` = no OpenAI (section 1 only). `false` = full report (needs `OPENAI_API_KEY`). |

### 1.5 API key (for full reports)

If `dry_run` is `false`, set `OPENAI_API_KEY` in a `.env` file in the `boss-assistant` folder (or in the system/user environment so the scheduled task can see it).

---

## 2. Run once (test)

From the `boss-assistant` folder with the venv activated:

```powershell
python run_automated.py
```

- With **inbox:** Put a CSV or JSON in `inbox/` first (e.g. copy `inbox/sample.csv`). You should see `Using latest file: ...` and then `Report written: ...\reports\report_YYYY-MM-DD_HH-MM.txt`.
- With **file:** Ensure `data.json` (or your `data_file`) exists. Same report output.

Open the report file to confirm it looks correct.

---

## 3. Schedule it (Windows Task Scheduler)

So it **runs by itself** (e.g. first Monday of the month at 8:00):

1. Open **Task Scheduler** (search “Task Scheduler” in Windows).
2. **Create Task** (not “Create Basic Task”).
3. **General:** Name e.g. “Vision Constructions Boss Report”. Run whether user is logged on or not if needed.
4. **Triggers:** e.g. **Monthly**, first Monday, 8:00 AM (or **Weekly** every Monday).
5. **Actions:** **Start a program**  
   - Program: full path to `Run_automated.bat` (e.g. `C:\...\boss-assistant\Run_automated.bat`).  
   - Start in: `C:\...\boss-assistant`
6. **Conditions:** Uncheck “Start only if on AC power” if the PC might be on battery.
7. **Settings:** Allow task to run on demand; optionally “Run as soon as possible after a missed start”.

If the task runs under a different user, set `OPENAI_API_KEY` in that user’s environment (or in System environment variables) so full reports work.

---

## 4. What “by itself” means now

| Step              | Who / what |
|-------------------|------------|
| Get numbers into a file | You (or bookkeeper): **save/export** a CSV or JSON into the **inbox** folder — no need to open the Boss Assistant or paste numbers. Optionally point an export from Xero/Excel to that folder. |
| Run the report   | Task Scheduler runs `Run_automated.bat` on the schedule. The script uses the **newest** file in the inbox (or the single data file if you use `data_source: "file"`). |
| Read the report  | Open the latest `report_*.txt` in the `reports` folder, or add a step to email it. |

So you get **access to files** (inbox or one data file) and it **works and runs by itself** without physically typing anything in — you only place a file (export/save/copy) and the schedule does the rest.
