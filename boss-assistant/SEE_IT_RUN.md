# See the Boss Assistant run (no code — just the result)

Right now the Boss Assistant **runs in the terminal** and **writes a report to a file**. There’s no website or app yet — you run a command and the report appears. Here’s how to see it.

---

## 1. Open PowerShell

Press **Windows key**, type **PowerShell**, press Enter.

---

## 2. Go to boss-assistant and turn on the venv

Copy and paste these two lines (one at a time, press Enter after each):

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\Activate.ps1
```

You should see `(.venv)` at the start of the line.

---

## 3. Run the report (and open it)

**Option A — Use example data and open the report when it’s done**

```powershell
python run.py --file data.example.json --dry-run
```

The **full report** will **print in the terminal** (Performance Summary, Likely Reasons, Boss To-Do List). That’s the report — scroll up if it’s long.

To **save** that same report to a file and **open the file** so you can read it in Notepad:

```powershell
python run.py --file data.example.json --dry-run > report.txt
notepad report.txt
```

**Option B — Use the automated run and open the report file**

This uses the **vision_data** folder (or inbox). If there’s no CSV/JSON there, copy the example first:

```powershell
copy vision_data\vision_12months.example.csv vision_data\vision_12months.csv
python run_automated.py --open
```

The report is written to **reports\report_YYYY-MM-DD_HH-MM.txt** and, with **--open**, the file **opens in Notepad** so you see the result.

---

## What you’re actually seeing

- **In the terminal:** The report text, or a line like `Report written: ...\reports\report_2025-02-23_14-30.txt`.
- **In Notepad (with --open or notepad report.txt):** The same report — Management report, Performance Summary, Likely Reasons, Boss To-Do List.

So **“how it runs”** = you run one command → the script reads the numbers → builds the report → prints it and/or saves it to a file. **“Seeing it”** = the text in the terminal or the opened .txt file. There’s no separate website or dashboard yet — that would be a next step (e.g. a simple page that runs the report and shows it in the browser).
