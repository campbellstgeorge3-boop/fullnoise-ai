INBOX — Boss Assistant automatic data

When auto_config.json has "data_source": "inbox", the scheduled run uses
the NEWEST .json or .csv file in this folder. No need to open the app or
paste numbers.

How to use:
- Export your figures from Excel/Xero/your system to a CSV or JSON file.
- Save or copy that file into this inbox folder (e.g. monthly_figures.csv).
- The scheduled task will pick the latest file and generate the report.

CSV format (with header row):
  revenue_this_month,revenue_last_month,budget_this_month,jobs_this_month,jobs_last_month,company_name,outstanding_quotes_count,overdue_invoices_count,notes

Or one row of numbers only (no header), in that order. See sample.csv.

JSON: same keys as data.example.json in the boss-assistant folder.
