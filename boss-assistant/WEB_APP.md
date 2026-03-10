# Boss Assistant — Web app

One server serves:

- **Landing page** — `GET /`  
  Public sales page: what the product does, how it works, pricing, contact form. Use this URL when sharing with prospects (e.g. with ngrok or your deployed URL).

- **Admin dashboard** — `GET /dashboard`  
  List clients and trigger “Send report” per client. Report runs in the background; check the server terminal for errors.

- **Reply-by-email** — `POST /api/inbound-email`  
  Resend webhook; no auth. Used when clients reply to report emails.

- **Client portal** — `GET /client`  
  Clients sign in with a magic link (email). They see their latest report and can ask questions in the browser. Same data as reply-by-email; two ways to interact.

**Client portal setup:** Set `SESSION_SECRET` in `.env` to a long random string (e.g. 32+ chars). This signs the session cookie so clients stay logged in. Magic links are sent via Resend (same as report emails). The landing page has a “Client sign in” link; clients use the email address where they receive their report.

## Run as a desktop app (no PowerShell)

**Double-click** one of these in the `boss-assistant` folder:

- **`Start_Boss_Assistant.vbs`** — Starts the app with no console window at all. A small “Boss Assistant” window appears; the browser opens to the landing page. Click **Stop server** or close the window when you’re done.
- **`Start_Boss_Assistant.bat`** — Same as above; you may see a brief console flash before the app window appears.

No copying/pasting into PowerShell, no window to keep open. The small app window has **Open in browser** and **Stop server**; closing it stops the server.

## Run from terminal (optional)

```bash
cd boss-assistant
.venv\Scripts\activate
uvicorn chat_server:app --host 0.0.0.0 --port 8001
```

- Landing: http://localhost:8001/
- Dashboard: http://localhost:8001/dashboard
- Health: http://localhost:8001/health

## Dashboard password (optional)

To protect the dashboard (and `/api/clients`, `/api/run-client`) with a password, add to `.env`:

```env
DASHBOARD_PASSWORD=your-secret-password
```

If set, the browser will prompt for username/password when visiting `/dashboard`. Use any username (e.g. `admin`) and the password you set.

## Contact form on the landing page

The “Get started” form sends to `POST /api/contact` and emails you the lead. Set `CONTACT_EMAIL_TO` in `.env` (or the first `REPORT_EMAIL_TO` is used).

## Deploying

Deploy the same app (e.g. Railway, Fly.io) and set:

- `RESEND_API_KEY`, `OPENAI_API_KEY`, `REPORT_EMAIL_FROM`
- Optional: `CONTACT_EMAIL_TO`, `DASHBOARD_PASSWORD`, `SESSION_SECRET` (required for client portal)
- Resend webhook URL: `https://your-domain.com/api/inbound-email`

Then use `https://your-domain.com` as your landing page and `https://your-domain.com/dashboard` for the admin dashboard.
