# Deploy FullNoise — exact copy & paste

Do the steps in order. Where it says "you get this from…", do that step first and paste the result.

---

## STEP 1: Railway — New project

1. Open: **https://railway.app**
2. Sign in (e.g. GitHub).
3. Click **"New Project"**.
4. Click **"Deploy from GitHub repo"** → choose your repo (e.g. `shopping-agent-real` or whatever it’s called). If you don’t see it, connect GitHub first.
5. Railway creates one service. Leave it for now.

---

## STEP 2: Railway — Add Postgres and Redis

1. In the project, click **"+ New"** (or "Add a service").
2. Click **"Database"** → **"Add PostgreSQL"**. Wait until it’s created.
3. Click **"+ New"** again → **"Database"** → **"Add Redis"**. Wait until it’s created.
4. You should now see: your repo service + Postgres + Redis.

---

## STEP 3: Railway — Get DATABASE_URL

1. Click the **Postgres** service (the database, not your code).
2. Open the **"Variables"** or **"Connect"** tab.
3. Find **`DATABASE_URL`** or a connection string that starts with `postgresql://`.
4. **Copy the full URL.** It might look like:  
   `postgresql://postgres:xxxxx@containers-us-west-xxx.railway.app:5432/railway`
5. In a text editor, change the **very start** from `postgresql://` to `postgresql+asyncpg://` (add `+asyncpg`).  
   Example:  
   `postgresql+asyncpg://postgres:xxxxx@containers-us-west-xxx.railway.app:5432/railway`
6. **Copy that modified URL** — you’ll paste it in Step 5.

---

## STEP 4: Railway — Get REDIS_URL

1. Click the **Redis** service.
2. Open **"Variables"** or **"Connect"**.
3. Find **`REDIS_URL`** or a URL that starts with `redis://` or `rediss://`.
4. **Copy the full value** — you’ll paste it in Step 5.

---

## STEP 5: Railway — Configure the API service

1. Click the **service that’s your code** (the one from GitHub), not Postgres or Redis.
2. Go to **"Settings"** (or the service name → Settings).
3. Find **"Root Directory"** (or "Source").  
   - Set it to: **`fullnoise/fullnoise-api`**  
   - (If your repo has no `fullnoise` folder and the API is at the root, use **`fullnoise-api`** or leave blank if the repo root is the API.)
4. Find **"Build Command"**. You can leave empty if Railway uses the Dockerfile, or set to:  
   **`pip install -r requirements.txt`**
5. Find **"Start Command"** or **"Run"**. Set it to exactly:  
   **`uvicorn app.main:app --host 0.0.0.0 --port $PORT`**
6. Go to **"Variables"** (or "Environment"). Add these **one by one** (name = Key, value = Value):

   | Key (name) | Value (paste this) |
   |------------|--------------------|
   | `DATABASE_URL` | The **modified** Postgres URL from Step 3 (with `postgresql+asyncpg://`) |
   | `REDIS_URL` | The Redis URL you copied in Step 4 |
   | `NEXTAUTH_SECRET` | `hti+utj17snjXRxQIESIcJEEm55kGS66riBTYs6dXSY=` |
   | `OPENAI_API_KEY` | Your real OpenAI key (starts with `sk-`) |
   | `RESEND_API_KEY` | Your real Resend API key (starts with `re_`) |
   | `RESEND_FROM_EMAIL` | Your verified sender email, e.g. `reports@yourdomain.com` |
   | `FRONTEND_URL` | Leave as `https://placeholder.vercel.app` for now — you’ll change it after Vercel |
   | `ADMIN_EMAIL` | `admin@fullnoise.ai` (or any email you want for admin login) |
   | `ADMIN_PASSWORD` | `admin` (or a password you choose) |

7. Save. Then open **"Settings"** again and find **"Generate domain"** or **"Public networking"** → generate a public URL.
8. **Copy that URL** (e.g. `https://fullnoise-api-production-xxxx.up.railway.app`). This is your **Railway API URL**. You’ll use it in Vercel and Resend.

---

## STEP 6: Railway — Add the worker

1. In the **same** Railway project, click **"+ New"**.
2. Choose **"GitHub Repo"** and select the **same repo** as the API.
3. After it’s added, click that **new service**.
4. **Settings** → **Root Directory**: **`fullnoise/fullnoise-api`** (same as API).
5. **Start Command**: **`arq app.worker.WorkerSettings`**
6. **Variables**: Add the **exact same** variables as in Step 5 (same keys and values). Easiest: copy from the API service if Railway has “Copy from another service,” or paste each one again.
7. Deploy. No need to generate a domain for the worker.

---

## STEP 7: Vercel — Deploy the web app

1. Open: **https://vercel.com**
2. Sign in (e.g. GitHub).
3. Click **"Add New"** → **"Project"**.
4. Import your **same repo**. Next.
5. **Root Directory**: click **"Edit"** and set to **`fullnoise/fullnoise-web`** (or `fullnoise-web` if that’s the folder with `package.json`).
6. **Environment Variables** — add these (key = Name, value = Value):

   | Name | Value |
   |------|--------|
   | `NEXT_PUBLIC_API_URL` | Your **Railway API URL** from Step 5 (e.g. `https://fullnoise-api-production-xxxx.up.railway.app`) — no slash at the end |
   | `NEXTAUTH_SECRET` | `hti+utj17snjXRxQIESIcJEEm55kGS66riBTYs6dXSY=` |
   | `NEXTAUTH_URL` | Leave blank for now; Vercel will suggest it, or you’ll paste after deploy (e.g. `https://your-project.vercel.app`) |

7. Click **"Deploy"**. Wait until it’s done.
8. Copy your **Vercel URL** (e.g. `https://fullnoise-web-xxx.vercel.app`). This is your **live site**.

---

## STEP 8: Set FRONTEND_URL on Railway

1. Go back to **Railway** → your **API** service (the one running uvicorn).
2. **Variables** → find **`FRONTEND_URL`**.
3. Change its value from `https://placeholder.vercel.app` to your **Vercel URL** (e.g. `https://fullnoise-web-xxx.vercel.app`). No trailing slash.
4. Save. Railway will redeploy the API.

---

## STEP 9: Set NEXTAUTH_URL on Vercel (if needed)

1. Go to **Vercel** → your project → **Settings** → **Environment Variables**.
2. If **`NEXTAUTH_URL`** is empty, add it: **Name** `NEXTAUTH_URL`, **Value** your Vercel URL (e.g. `https://fullnoise-web-xxx.vercel.app`).
3. Save. Optionally trigger a redeploy so the app picks it up.

---

## STEP 10: Resend — Inbound webhook

1. Open: **https://resend.com** (log in to the account where your domain is verified).
2. Go to **Inbound** (or **Receiving** / **Webhooks**).
3. Add or edit the **webhook URL**. Set it to exactly:  
   **`https://YOUR-RAILWAY-API-URL/webhooks/resend/inbound`**  
   Replace `YOUR-RAILWAY-API-URL` with your real Railway API URL (no trailing slash).  
   Example: **`https://fullnoise-api-production-xxxx.up.railway.app/webhooks/resend/inbound`**
4. Save.

---

## Test

1. Open your **Vercel URL** in the browser.
2. Click **Sign in** → **Admin** tab.
3. Email: **`admin@fullnoise.ai`** (or whatever you set for `ADMIN_EMAIL`).  
   Password: **`admin`** (or whatever you set for `ADMIN_PASSWORD`).
4. Add a client (your real email), click **Send report**, check your inbox for the report.
5. Reply to that email with a question; you should get a reply back.

---

## Quick reference — what goes where

| What | Where it goes |
|------|----------------|
| `postgresql+asyncpg://...` (from Postgres) | Railway API + Worker → `DATABASE_URL` |
| Redis URL | Railway API + Worker → `REDIS_URL` |
| `hti+utj17snjXRxQIESIcJEEm55kGS66riBTYs6dXSY=` | Railway API + Worker → `NEXTAUTH_SECRET`; Vercel → `NEXTAUTH_SECRET` |
| OpenAI key `sk-...` | Railway API + Worker → `OPENAI_API_KEY` |
| Resend key `re_...` | Railway API + Worker → `RESEND_API_KEY` |
| Your Vercel URL | Railway API → `FRONTEND_URL`; Vercel → `NEXTAUTH_URL` |
| Your Railway API URL | Vercel → `NEXT_PUBLIC_API_URL`; Resend webhook URL = `https://RAILWAY_API_URL/webhooks/resend/inbound` |
