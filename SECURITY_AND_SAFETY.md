# Security & safety checklist

This document summarizes how the Shopping Agent and sales platform are kept safe and secure.

---

## Agent (Python)

### No credentials stored
- **We never see or store your Woolworths or Coles password.** You log in in the browser; the agent only keeps a browser profile (cookies/session) so you may stay logged in next time.
- No API keys or secrets in the agent code. `config.json` and `profile.json` only hold preferences (people, days, budget, avoid list, substitutions).

### Safe file paths
- All reads/writes are under the **agent folder** (where `agent.py` lives): `config.json`, `profile.json`, `cart.json`, `run_logs/`, `.browser_woolies/`, `.browser_coles/`.
- Paths are built from `Path(__file__).resolve().parent`, so even if you run the script from another directory, it won’t write files elsewhere.

### Config validation
- Values from `config.json` (people, days, budget) are checked and clamped to safe ranges (e.g. people 1–10, days 1–14, budget $10–$5000). Invalid or missing values fall back to defaults.

### Profile size cap
- `learned_failures` in `profile.json` is capped to the last 100 entries so the file doesn’t grow without limit. Error strings are truncated to 500 characters.

### No code execution from user input
- User input is only used for: numbers (recipe picks, remove items), yes/no, and short text (avoid list, people/days/budget). Nothing is passed to `eval()`, `exec()`, or shell commands.
- Cart item names sent to the browser come from the recipe data and substitutions, not raw user text (avoid list is only used to filter out ingredients).

---

## Sales platform (Next.js + Stripe)

### Secrets only on the server
- `STRIPE_SECRET_KEY` and `DOWNLOAD_URL` are **never** sent to the browser. They are only used in API routes (`create-checkout`, `verify-session`).
- The client only gets: the Stripe Checkout URL (from your server) and, after payment, the download URL (only after server-side verification).

### Payment verification before download
- The success page calls `/api/verify-session?session_id=...`. The server:
  1. Retrieves the Stripe Checkout session.
  2. Ensures `payment_status === "paid"`.
  3. Ensures `metadata.product === "shopping-agent"` (so only your product’s sessions get the download link).
- Only then is the download URL returned. Without a valid, paid session for this product, the API returns 403.

### No sensitive errors to the client
- The create-checkout API returns a generic message (“Checkout failed. Please try again.”) on 500 errors, so Stripe or internal details are not exposed.

### Session ID checks
- `session_id` from the URL is length-limited (max 200 characters) before calling Stripe, to avoid abuse.

---

## What to exclude when sharing

- **Don’t share:** `.venv/`, `profile.json`, `cart.json`, `run_logs/`, `.browser_woolies/`, `.browser_coles/`, `.env`, `.env.local`.
- A root `.gitignore` is set so these are not committed if you use Git. When sending the agent as a zip, only include the code and docs (see `SHARING_AND_SELLING.md`).

---

## Summary

| Area              | What we do |
|-------------------|------------|
| Passwords         | Never stored or read; user logs in in the browser only. |
| File paths        | All under the agent directory; no path traversal. |
| Config/profile    | Validated and clamped; profile size capped. |
| Sales platform    | Stripe secret and download URL server-side only; download only after verified payment and product metadata check. |

If you add new features (e.g. new config keys or API routes), keep these rules in mind: no credentials in code or client, validate inputs, and keep file operations under a known base directory.
