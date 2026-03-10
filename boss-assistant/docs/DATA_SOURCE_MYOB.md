# Data from MYOB (direct — saleable agent)

With **data_source: "myob"**, the Boss Assistant pulls **revenue** straight from the client’s MYOB (AccountRight / Business API). They connect MYOB once; after that the agent gets this month and last month revenue automatically. No file uploads.

---

## What comes from MYOB

- **Revenue this month** and **revenue last month** — from the MYOB Profit & Loss report for the current and previous calendar month.
- **Budget** and **jobs completed** — MYOB P&L doesn’t provide these. You can:
  - Set them in config (`myob_budget`, `myob_jobs_this`, `myob_jobs_last`) if the client gives you numbers, or
  - Leave them 0; the report will still show revenue and % change.

---

## One-time setup (per client)

### 1. Register an app with MYOB

1. Go to [developer.myob.com](https://developer.myob.com) and sign in.
2. Create an API key (Company File / AccountRight or Business API).
3. Note: **API Key**, **API Secret**, and a **Redirect URI** (e.g. `https://yoursite.com/myob-callback` or `http://localhost:8080/myob-callback` for testing).

### 2. Client connects MYOB (OAuth once)

The client must authorise your app once so you get a **refresh token**:

1. Send them to (or open for them):
   ```
   https://secure.myob.com/oauth2/account/authorize?client_id=YOUR_API_KEY&redirect_uri=YOUR_REDIRECT_URI&response_type=code&scope=CompanyFile
   ```
   (Use the scope your app needs; e.g. `CompanyFile` or the scope that includes Reports.)

2. They sign in to MYOB and approve; the browser redirects to your `redirect_uri` with `?code=...&businessId=...` in the URL.

3. Exchange the `code` for tokens (POST to `https://secure.myob.com/oauth2/v1/authorize` with `grant_type=authorization_code`, `code`, `client_id`, `client_secret`, `redirect_uri`). The response includes **access_token** and **refresh_token**.

4. Save:
   - **refresh_token** — for your automated runs (store in `.env` or your secrets).
   - **businessId** — this is the `cf_uri` (company file identifier) for API calls.

### 3. Config and env (boss-assistant)

**auto_config.json** (copy from `auto_config.myob.example.json`):

- `"data_source": "myob"`
- `"myob_cf_uri": "<businessId from step 2>"`
- `"company_name": "Client Name"`
- Optional: `myob_budget`, `myob_jobs_this`, `myob_jobs_last` (or leave 0).

**.env** (never commit):

- `MYOB_REFRESH_TOKEN=<refresh_token from step 2>`
- `MYOB_CLIENT_ID=<your API Key>`
- `MYOB_CLIENT_SECRET=<your API Secret>`
- `MYOB_API_KEY=<your API Key again (x-myobapi-key)>`

You can use different env var names and set `myob_refresh_token_env`, `myob_client_id_env`, etc. in config to match.

### 4. Run

```powershell
python run_automated.py
```

The agent will use the refresh token to get an access token, call MYOB for P&L for this month and last month, sum revenue, and build the report. No file from the client.

---

## Jobs and budget

- **Jobs completed** — Not in MYOB P&L. Either the client gives you the numbers and you set `myob_jobs_this` / `myob_jobs_last` in config (or via a small script that updates config), or you leave them 0 and the report focuses on revenue.
- **Budget** — Set `myob_budget` in config if the client has a monthly budget figure; otherwise leave 0.

Later you can add a second source (e.g. job software) for jobs, or a budget API.

---

## Summary

- **Revenue:** Pulled from MYOB each run (this month + last month).
- **Client:** Connects MYOB once (OAuth); you store refresh_token and cf_uri.
- **No files:** Agent gets data straight from MYOB; no CSV or manual entry.
- **Jobs/budget:** Optional in config or left 0.

This gives you **data straight out of MYOB** for the saleable agent.
