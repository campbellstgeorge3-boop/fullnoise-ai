# Best: Data from API (client never puts files in)

With **data_source: "api"**, the agent **pulls** the numbers from a URL each run. The client doesn’t upload or edit any file after the first setup.

---

## How it works

1. **You (or the client) set up a single endpoint** that returns JSON in this shape:
   ```json
   {
     "revenue_this_month": 185000,
     "revenue_last_month": 210000,
     "budget_this_month": 200000,
     "jobs_this_month": 12,
     "jobs_last_month": 14
   }
   ```
   Optional: `company_name`, `outstanding_quotes_count`, `overdue_invoices_count`, `notes`.

2. **In auto_config.json** you set:
   - `"data_source": "api"`
   - `"api_url": "https://..."` (the URL above)
   - Optional: `"api_key_env": "BOSS_API_KEY"` — then the app sends `Authorization: Bearer <value from .env>` so the URL can be protected.

3. **Each run** (scheduled or manual), the agent **GETs that URL**, gets the JSON, builds the report. No file drop, no typing.

So the client (or their system) only has to **expose that URL once**; the agent keeps pulling from it.

---

## Where the URL can come from

- **Zapier / Make / n8n** — Trigger: “every month” or “when Xero closes month.” Action: get revenue/jobs from Xero (or spreadsheet), build the JSON, send to a “webhook” or “store in a small app” that serves it at a URL. Boss Assistant then points at that URL.
- **Your own small server** — A tiny API (e.g. Flask/Next.js) that reads from the client’s Xero (or DB) and returns the JSON. You host it; client connects Xero once to your app.
- **Direct Xero (later)** — A **Xero connector** can be added: client signs in with Xero once (OAuth), we store a token and pull P&L (revenue) + budget from Xero each run. Then you don’t need a separate URL; the agent talks to Xero directly. Jobs completed may come from job software (Jobpac, Aroflo) or stay optional. That’s the next step after “API URL.”

---

## Setup steps (API URL)

1. Copy `auto_config.api.example.json` to `auto_config.json` (or merge the api bits into your existing config).
2. Set `api_url` to the URL that returns the JSON above.
3. If the URL requires a secret, set `api_key_env` to the name of an env var (e.g. `BOSS_API_KEY`) and put that value in `.env`.
4. Run `python run_automated.py` — the agent will fetch from the API and generate the report.

No file in the inbox, no manual data entry. That’s the “best” setup: **connect once (or expose one URL), agent pulls forever.**
