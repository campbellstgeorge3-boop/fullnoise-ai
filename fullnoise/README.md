# FullNoise AI

SaaS “Boss Assistant”: monthly financial reports by email and Q&A via reply or web portal.

## Stack

- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind, NextAuth (magic link for clients, credentials for admin).
- **Backend:** FastAPI, OpenAI, Resend, Postgres, background worker (ARQ + Redis).

## Quick start (local)

### 1. Database and Redis

From this directory:

```bash
cd docker
docker compose up -d
```

Then set in `fullnoise-api/.env`:

- `DATABASE_URL=postgresql+asyncpg://fullnoise:fullnoise@localhost:5432/fullnoise`
- `REDIS_URL=redis://localhost:6379/0`

### 2. API

```bash
cd fullnoise-api
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
cp .env.example .env      # edit with your keys
uvicorn app.main:app --reload --port 8000
```

### 3. Worker (separate terminal)

```bash
cd fullnoise-api
.venv\Scripts\activate
arq app.worker.WorkerSettings
```

### 4. Web

```bash
cd fullnoise-web
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000, NEXTAUTH_SECRET
npm run dev
```

Open http://localhost:3000. Admin: use the email/password from `ADMIN_EMAIL` / `ADMIN_PASSWORD` in the API `.env`. Clients: request a magic link from the login page.

## Deploy (Railway / Render + Vercel)

See **[docs/deploy.md](docs/deploy.md)** for step-by-step deployment of the API and worker (Railway or Render with Postgres + Redis) and the Next.js web app (Vercel). After deploy, set Resend’s inbound webhook to `https://your-api-url/webhooks/resend/inbound`; see [docs/resend-reply-setup.md](docs/resend-reply-setup.md) for reply-to-email setup.

## Project layout

- `fullnoise-api/` — FastAPI app, auth, report/ask services, ARQ worker.
- `fullnoise-web/` — Next.js app, landing, login, client report/ask, admin client list.
- `docker/` — docker-compose for Postgres and Redis.
