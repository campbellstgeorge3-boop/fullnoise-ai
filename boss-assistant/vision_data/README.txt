VISION CONSTRUCTIONS — Put your data files here

The Boss Assistant will use the NEWEST .csv or .json file in this folder.
You don't type any numbers — just put your export or spreadsheet save here.

WHAT TO PUT HERE
----------------
• A CSV or JSON file with Vision's figures (revenue, jobs, budget).
• You can put multiple files; the app uses the one with the newest "modified" date.

TWO FORMATS THAT WORK
---------------------
1) Single report (this month vs last month)
   CSV with header and one data row:
   revenue_this_month,revenue_last_month,budget_this_month,jobs_this_month,jobs_last_month
   Example: 185000,210000,200000,12,14

   Or a JSON file with those same keys (see data.example.json in boss-assistant).

2) Full history (12 months)
   CSV with header and one row per month (oldest first):
   month,revenue,jobs_completed,budget
   2024-01,180000,10,200000
   2024-02,192000,11,200000
   ...
   2024-12,185000,12,200000
   Save as e.g. vision_12months.csv in this folder.
   Then run: python run_from_history.py --file vision_data/vision_12months.csv

SETUP
-----
1. Copy auto_config.example.json to auto_config.json (in boss-assistant folder).
2. Open auto_config.json and set: "inbox_dir": "vision_data"
3. Put your latest CSV or JSON in this vision_data folder.
4. Run: python run_automated.py
   (Or schedule Run_automated.bat in Task Scheduler — it will use the newest file here.)

Reports are saved to the "reports" folder in boss-assistant.
