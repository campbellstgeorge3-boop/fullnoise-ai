# Boss Assistant — Security & correctness audit

Checked: config, secrets, client data flow, validation, and email behaviour. Summary below.

---

## Security

### Secrets
- **API keys** are read from `.env` (OPENAI_API_KEY, RESEND_API_KEY). Not hardcoded.
- **Root repo** `.gitignore` includes `.env` and `.env.local`, so secrets are not committed.
- **boss-assistant** has its own `.gitignore` that ignores `.env`, `tokens/`, and local env files so nothing sensitive is added from this folder.

### Config
- **clients.json** holds client config (ids, emails, paths). No API keys. Safe to commit if you redact real emails for a public repo.
- **Token files** (e.g. `tokens/default_drive_token.json`) are in `tokens/` and ignored via `.gitignore`.

### Recommendations
- Do not commit `.env`. If you ever did, rotate both API keys and ensure `.env` is in `.gitignore`.
- Keep `clients.json` in version control only if it does not contain data you consider confidential; otherwise add it to `.gitignore` or use a template.

---

## Correctness

### main.py —run-client
- Loads **clients.json** from the same directory as `main.py`.
- Finds client by `id`; requires **csv_path** and uses **email_to** and **recipient_first_name**.
- Sets `args.csv`, `args.email`, `args.run_now` and passes **email_to** into `send_report_email` and **send_abort_alert_email** so the right client gets the report or abort alert.
- **CSV path**: checked with `args.csv.exists()` before loading; clear error if missing.
- **Recipient**: when `run_client_recipient` is set, it overrides `recipient_first_name` for the email.

### emailer.py
- **send_report_email**: uses **email_to** when provided (e.g. from client config); otherwise uses REPORT_EMAIL_TO from env. No mix-up between clients.
- **Domain fallback**: if sending fails with “not verified”, it retries once from `onboarding@resend.dev` so the report still sends. No silent failure.
- **send_abort_alert_email**: now accepts optional **email_to**; when validation fails in `--run-client` mode, the abort alert goes to that client’s email instead of only REPORT_EMAIL_TO.

### data_loader.py
- **load_from_12month_csv**: expects columns `month`, `revenue`, `jobs`; optional `budget`, `costs`. Uses last two rows for “this” and “last” month. Handles missing/zero budget and jobs.
- **Validation** in main allows `budget_this_month >= 0` and `jobs_this_month >= 0` (zero allowed), so CSVs with no budget/jobs columns still pass.

### Models
- **utils.BossInput** (main, emailer, data_sources) and **input_model.BossInput** (data_loader) both define the same core fields. main converts from data_loader’s result via `validate_and_parse(...)` so the rest of the pipeline uses a single, validated shape. No type mismatch in the flow.

---

## Behaviour summary

| Item | Status |
|------|--------|
| Secrets in .env only | OK |
| .env and tokens gitignored | OK |
| --run-client uses client csv_path and email_to | OK |
| Abort alert goes to client when using --run-client | OK (fixed) |
| Report email uses client email_to | OK |
| Fallback sender on domain error | OK |
| CSV validation allows 0 budget/jobs | OK |
| clients.json path and structure | OK |

---

## What to do regularly

1. **Run:** `python main.py --run-client default` and confirm the report sends and, if you force invalid data, that the abort email goes to the client.
2. **Keep .env out of git** and rotate keys if it was ever committed.
3. **Back up clients.json** if it’s the source of truth for client list and emails.
