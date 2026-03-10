# Run FullNoise API without Docker (Windows)

If you don't have Docker, use free cloud Postgres and Redis so the API and worker can start.

## 1. Postgres (database)

**Option A: Neon (recommended, free tier)**

1. Go to [neon.tech](https://neon.tech) and sign up.
2. Create a new project and a database.
3. In the dashboard, open **Connection details**.
4. Copy the connection string. It may look like:
   `postgresql://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require`
5. For this app, use the **async** form. Change the scheme to `postgresql+asyncpg` and keep the rest:
   ```text
   postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/neondb?sslmode=require
   ```
6. Put that in your `.env` as `DATABASE_URL`.

**Option B: Supabase**

1. Go to [supabase.com](https://supabase.com), create a project.
2. In **Project Settings → Database** copy the **Connection string** (URI).
3. Replace the scheme with `postgresql+asyncpg` (e.g. `postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:6543/postgres`).
4. Set that as `DATABASE_URL` in `.env`.

## 2. Redis (job queue)

**Upstash (free tier)**

1. Go to [upstash.com](https://upstash.com) and sign up.
2. Create a **Redis** database (choose a region).
3. In the database dashboard, copy the **REST URL** or the **Redis URL** (e.g. `rediss://default:xxx@xxx.upstash.io:6379`).
4. Put it in `.env` as `REDIS_URL`. If Upstash gives you a REST URL, use the **Redis** tab and copy the URL that starts with `rediss://` or `redis://`.

## 3. Update your `.env`

In `fullnoise-api\.env`, set:

```env
DATABASE_URL=postgresql+asyncpg://YOUR_NEON_OR_SUPABASE_URL
REDIS_URL=rediss://default:YOUR_PASSWORD@YOUR_UPSTASH_HOST:6379
```

Keep your existing `NEXTAUTH_SECRET`, `OPENAI_API_KEY`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, and `FRONTEND_URL`.

## 4. Start the API and worker

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-api
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

In a second terminal (worker):

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-api
.\.venv\Scripts\Activate.ps1
arq app.worker.WorkerSettings
```

The API will create tables on first run. Then you can use the scripts (e.g. send-me-a-report) and the web app.
