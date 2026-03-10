# Best path: Deploy, then use it

**Recommendation:** Deploy the API + worker to **Railway** and the web app to **Vercel**. You get a live site and reply-to-email works without any local setup. Then "run it" = open the URL and use it.

---

## 1. Run the build (on your machine)

In PowerShell, from the repo:

```powershell
# Build the web app (checks it compiles)
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-web
npm install
npm run build
```

If that succeeds, the frontend is ready to deploy.

---

## 2. Deploy (what to do)

### A. Railway – API + Worker

1. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub** (connect repo if needed).
2. **+ New** → **PostgreSQL**; then **+ New** → **Redis**.
3. **+ New** → **GitHub Repo** → same repo. Set **Root Directory** to `fullnoise/fullnoise-api` (if your repo root is `shopping-agent-real`).
4. For this service (API): **Settings** → **Build** → leave default or `pip install -r requirements.txt`. **Start** → `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
5. **Variables**: Add all from the table in [docs/deploy.md](docs/deploy.md). For `DATABASE_URL`: from Postgres service copy the URL and change `postgresql://` to `postgresql+asyncpg://`. For `REDIS_URL`: copy from Redis service.
6. **Generate domain** for this service and copy the URL (e.g. `https://fullnoise-api.up.railway.app`).
7. **+ New** → **Empty Service** (or same repo again). **Root Directory** `fullnoise/fullnoise-api`. **Start** → `arq app.worker.WorkerSettings`. **Variables** → same as API (or reference the API’s vars). No public URL needed.

### B. Vercel – Web

1. Go to [vercel.com](https://vercel.com) → **Add New** → **Project** → import your repo.
2. **Root Directory** → `fullnoise/fullnoise-web`.
3. **Environment Variables**:  
   `NEXT_PUBLIC_API_URL` = your Railway API URL  
   `NEXTAUTH_SECRET` = same long random string you used on Railway  
   `NEXTAUTH_URL` = your Vercel URL (e.g. `https://your-project.vercel.app`)
4. Deploy. Copy the Vercel URL.

### C. Wire it up

- On **Railway** (API service): set `FRONTEND_URL` = your Vercel URL. Redeploy if needed.
- In **Resend**: Inbound webhook URL = `https://YOUR-RAILWAY-API-URL/webhooks/resend/inbound`.

---

## 3. Run it (use it)

- Open your **Vercel URL**.
- **Admin:** Sign in with the Admin tab (email/password from `ADMIN_EMAIL` / `ADMIN_PASSWORD`).
- Add a client, send a report, then reply to the email to test reply-to-email.

That’s the best path: deploy once, then “run” = use the live site.
