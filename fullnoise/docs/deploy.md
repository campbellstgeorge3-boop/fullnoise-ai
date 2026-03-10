# Deploy FullNoise AI

Get the API, worker, and web app live so you can use the site and test reply-to-email end-to-end.

---

## Quick checklist (do in order)

1. **Create a secret** — Use the same value for API and Vercel. Example: open PowerShell and run `[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])` and copy the result, or use any 32+ character random string (e.g. `fullnoise-my-secret-key-xyz-12345`).
2. **Railway** — [railway.app](https://railway.app) → New Project → add **PostgreSQL** and **Redis** → deploy your repo with **Root Directory** `fullnoise/fullnoise-api` → set **Start** to `uvicorn app.main:app --host 0.0.0.0 --port $PORT` → add all **Variables** (see table below; use `postgresql+asyncpg://...` for `DATABASE_URL`) → **Generate domain** for the API → copy the API URL.
3. **Railway worker** — In the same project, **+ New** → same repo, **Root Directory** `fullnoise/fullnoise-api`, **Start** `arq app.worker.WorkerSettings`, same **Variables** as the API → deploy.
4. **Vercel** — [vercel.com](https://vercel.com) → Import repo → **Root Directory** `fullnoise/fullnoise-web` → add **Environment Variables**: `NEXT_PUBLIC_API_URL` = your Railway API URL, `NEXTAUTH_SECRET` = the secret from step 1, `NEXTAUTH_URL` = your Vercel URL (e.g. `https://your-project.vercel.app`) → Deploy → copy the Vercel URL.
5. **Railway API again** — Set `FRONTEND_URL` = your Vercel URL (so CORS and magic links work). Redeploy the API service if needed.
6. **Resend** — Dashboard → Inbound webhook URL = `https://YOUR-RAILWAY-API-URL/webhooks/resend/inbound`. Save.

Then open your Vercel URL, sign in (Admin tab) with `ADMIN_EMAIL` / `ADMIN_PASSWORD`, add a client, click “Send report,” and reply to the email to test.

---

## Overview

- **API + Worker**: Railway or Render (Postgres + Redis + two services).
- **Web (Next.js)**: Vercel.
- **Resend**: Inbound webhook points at your API URL.

Use the same `NEXTAUTH_SECRET` for API and web (e.g. generate one: `openssl rand -base64 32` or any 32+ character random string). Set `FRONTEND_URL` on the API to your Vercel URL.

**Repo layout:** If your repo root contains a `fullnoise` folder, set **Root Directory** to `fullnoise/fullnoise-api` (API/worker) and `fullnoise/fullnoise-web` (Vercel) when configuring the services.

---

## Option A: Railway (API + Worker)

### 1. Push your code

Ensure the FullNoise repo is on GitHub (or another Git host Railway can use).

### 2. Create a Railway project

1. Go to [railway.app](https://railway.app) and sign in (e.g. with GitHub).
2. **New Project** → **Deploy from GitHub repo** → select your repo.
3. Railway may detect one service. We’ll add Postgres, Redis, and a second service (worker).

### 3. Add Postgres and Redis

1. In the project, click **+ New** → **Database** → **PostgreSQL**. Add it.
2. **+ New** → **Database** → **Redis**. Add it.
3. Click the **Postgres** service → **Variables** (or **Connect**) and copy the `DATABASE_URL` (or use the “Variable” reference Railway shows).  
   **Important:** The app uses the **async** driver. If the URL is `postgresql://...`, change it to `postgresql+asyncpg://...` (same rest of URL) and set that as `DATABASE_URL` in the API service.
4. Click the **Redis** service → copy or reference `REDIS_URL` (often `redis://default:...@...railway.internal:6379` or a public URL).

### 4. API service (web)

1. In the project, add (or use) a service that runs your **API**.
2. If the repo root is the repo root (not `fullnoise-api`), set **Root Directory** to `fullnoise-api` (or wherever the API code lives).
3. **Settings** (or **Variables**):
   - **Build:** (optional) `pip install -r requirements.txt` if not using Dockerfile.
   - **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (Railway sets `PORT`).
4. **Variables** – add (or “reference” from Postgres/Redis where possible):

   | Variable | Value / note |
   |----------|------------------|
   | `DATABASE_URL` | Postgres URL with `postgresql+asyncpg://` |
   | `REDIS_URL` | From Redis service |
   | `NEXTAUTH_SECRET` | Same long random string you’ll use on Vercel |
   | `OPENAI_API_KEY` | Your OpenAI key |
   | `RESEND_API_KEY` | From Resend (same account as domain) |
   | `RESEND_FROM_EMAIL` | e.g. `reports@yourdomain.com` (verified domain) |
   | `FRONTEND_URL` | Your Vercel URL, e.g. `https://fullnoise.vercel.app` |
   | `ADMIN_EMAIL` | Admin login email |
   | `ADMIN_PASSWORD` | Admin login password |

5. Deploy. Copy the **public URL** of this service (e.g. `https://fullnoise-api.up.railway.app`). You’ll use it as the API base URL for the web app and for Resend.

### 5. Worker service

1. In the same Railway project, **+ New** → **GitHub Repo** (same repo) or **Empty Service**.
2. If same repo: set **Root Directory** to `fullnoise-api`.
3. **Start Command:** `arq app.worker.WorkerSettings`
4. **Variables:** Add the **same** variables as the API (or use Railway “shared” / “reference” variables so DATABASE_URL, REDIS_URL, etc. are identical). The worker needs DB, Redis, Resend, and OpenAI to send reports.
5. Deploy. No public URL needed for the worker.

### 6. Resend inbound webhook

1. Resend dashboard → **Inbound** (or **Receiving**) → set webhook URL to:
   `https://YOUR-RAILWAY-API-URL/webhooks/resend/inbound`
2. Save. Replies to report emails will be sent to this URL.

---

## Option B: Render (API + Worker)

1. Go to [render.com](https://render.com) and connect your repo.
2. Create a **PostgreSQL** database and a **Redis** instance (dashboard or Blueprint). Note the **Internal** (or external) connection strings.
3. **Web Service** (API):
   - Repo, **Root Directory**: `fullnoise-api`.
   - **Build:** `pip install -r requirements.txt`
   - **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add **Environment Variables**: same as in the table above. For `DATABASE_URL`, if Render gives `postgresql://...`, change to `postgresql+asyncpg://...`.
4. **Background Worker** (worker):
   - Same repo, **Root Directory**: `fullnoise-api`.
   - **Start:** `arq app.worker.WorkerSettings`
   - Same env vars as the API (especially `DATABASE_URL`, `REDIS_URL`, `RESEND_*`, `OPENAI_API_KEY`).
5. Deploy the web service and copy its URL. Set **Resend inbound webhook** to `https://YOUR-RENDER-API-URL/webhooks/resend/inbound`.
6. Set **FRONTEND_URL** on the API to your Vercel URL.

---

## Deploy the web app (Vercel)

1. Go to [vercel.com](https://vercel.com) and import your repo.
2. **Root Directory:** set to `fullnoise-web` (or the folder that contains `package.json` for the Next app).
3. **Build:** `npm run build` (default).
4. **Environment Variables** (Production and Preview if you want):

   | Variable | Value |
   |----------|--------|
   | `NEXT_PUBLIC_API_URL` | Your API URL (e.g. `https://fullnoise-api.up.railway.app`) |
   | `NEXTAUTH_SECRET` | **Same** as on the API (long random string) |
   | `NEXTAUTH_URL` | Your Vercel URL (e.g. `https://fullnoise.vercel.app`) |

5. Deploy. Then set **FRONTEND_URL** on the API to this Vercel URL (e.g. `https://fullnoise.vercel.app`) and redeploy the API if needed.

---

## After deploy

1. Open the Vercel URL → **Login** → **Admin** tab: log in with `ADMIN_EMAIL` / `ADMIN_PASSWORD`.
2. Add a client (or use the script against the live API URL) and send a report. The worker will send the email.
3. Reply to that email with a question. Resend will call your API; you should get a reply email.

If replies don’t arrive, check Resend **Logs** and the API logs (Railway/Render) for errors. Ensure the inbound webhook URL is exactly `https://YOUR-API-URL/webhooks/resend/inbound` and that `RESEND_API_KEY` is from the same Resend account where the domain is verified.
