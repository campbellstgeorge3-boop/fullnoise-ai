# Getting paid (full setup)

**Goal:** Send reports from **reports@mail.fullnoises.com** and support reply-by-email. No shortcuts – everything set up properly.

Use **FULL_SETUP.md** for the step-by-step. When that’s done:

- Run: `python main.py --run-client default` (monthly or on schedule).
- Reports go out from your domain; clients can reply and get an automatic answer by email.
- Charge a monthly retainer for the scorecard (and the reply-by-email experience).

Adding more clients: add an entry in `clients.json` (id, name, email_to, csv_path, etc.) and run `python main.py --run-client THEIR_ID`.
