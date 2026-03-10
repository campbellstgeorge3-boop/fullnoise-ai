# Test run: data from Google Drive

With **data_source: "googledrive"**, the Boss Assistant loads the input from a **file or Google Sheet on Google Drive**. You set it up once; each run it downloads the file/Sheet and builds the report. Good for a test run without local files.

---

## What you need

1. **A CSV or JSON file** (or a **Google Sheet**) in Drive with your numbers:
   - **Single report:** one row (or JSON) with `revenue_this_month`, `revenue_last_month`, `budget_this_month`, `jobs_this_month`, `jobs_last_month`.
   - **12-month history:** CSV with header `month,revenue,jobs_completed,budget` and one row per month (oldest first).

2. **A Google Cloud service account** so the script can read from Drive:
   - Create a project in [Google Cloud Console](https://console.cloud.google.com).
   - Enable **Google Drive API**.
   - Create a **service account**, download its **JSON key**.
   - **Share** the Drive file or Sheet with the service account email (e.g. `xxx@project.iam.gserviceaccount.com`) as Viewer.

3. **The file or Sheet ID** from the sharing link.  
   For a link like `https://drive.google.com/file/d/ABC123xyz/view` or `https://docs.google.com/spreadsheets/d/ABC123xyz/edit`, the ID is **ABC123xyz**.

---

## Setup (test run)

### 1. Install Google dependencies

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\Activate.ps1
pip install google-auth google-api-python-client
```

### 2. Put your data in Drive

- Upload a **CSV** or **JSON** with the 5 numbers (see `data.example.json` or `inbox/sample.csv`), **or**
- Create a **Google Sheet** with the same columns (one header row, one data row for single report; or 12 rows for history).
- Share the file or Sheet with your **service account email** (from the JSON key: `client_email`) as **Viewer**.

### 3. Set the file ID and credentials

**Option A — Config only (file ID in config, credentials from env)**

- Copy `auto_config.googledrive.example.json` to `auto_config.json` (or merge into your existing config).
- Set `"data_source": "googledrive"` and `"googledrive_file_id": "YOUR_FILE_OR_SHEET_ID"`.
- In **.env** (or your environment), set:
  ```
  GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your-service-account-key.json
  ```
  (Use the full path to the JSON key file you downloaded.)

**Option B — Config for everything**

- In `auto_config.json` set:
  - `googledrive_file_id`: the Drive file or Sheet ID
  - `googledrive_credentials`: full path to the service account JSON file (optional; if empty, uses `GOOGLE_APPLICATION_CREDENTIALS`)

### 4. Run

```powershell
python run_automated.py
```

The agent will download the file (or export the Sheet as CSV), parse it, and generate the report. No local data file needed — all data comes from Google Drive for the test run.

---

## Getting the file ID

- **Drive file:** Open the file in Drive → Share → copy link. The ID is the long string between `/d/` and `/view` (or next `/`).
- **Google Sheet:** Same: open the sheet, copy link from the address bar. The ID is between `/d/` and `/edit`.

---

## Summary

| Step | What to do |
|------|------------|
| 1 | Put CSV/JSON or a Sheet in Drive with your numbers; share it with the service account email. |
| 2 | Set `GOOGLE_APPLICATION_CREDENTIALS` to the service account JSON path (or set `googledrive_credentials` in config). |
| 3 | Set `data_source: "googledrive"` and `googledrive_file_id` to the file/Sheet ID. |
| 4 | Run `python run_automated.py` — data is pulled from Drive for the test run. |
