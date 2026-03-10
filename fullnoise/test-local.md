# Test FullNoise locally

Use these steps on your machine (Docker Desktop and Node/Python installed).

## 1. Start Postgres and Redis

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\docker
docker compose up -d
```

Check: `docker compose ps` should show `postgres` and `redis` running.

## 2. Start the API

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-api
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- **.env** is already created with DB/Redis URLs matching docker-compose.
- Replace `OPENAI_API_KEY` and `RESEND_API_KEY` in `.env` with real keys for emails and report generation.
- Quick check: open http://localhost:8000/health — should return `{"status":"ok","service":"fullnoise-api"}`.

## 3. Start the worker (optional, for “Send report”)

In a **second** terminal:

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-api
.venv\Scripts\activate
arq app.worker.WorkerSettings
```

## 4. Start the web app

In a **third** terminal:

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-web
npm install
npm run dev
```

- **.env.local** is already created; it points at `http://localhost:8000` and uses the same `NEXTAUTH_SECRET` as the API.

Open http://localhost:3000.

## 5. What to test

1. **Landing** — Home, Pricing, Contact, Login.
2. **Admin** — Login with Admin tab: email `admin@fullnoise.ai`, password `admin` (or whatever you set in API `.env`). You should see the admin clients list; add a client via API or DB, then “Send report” (worker must be running).
3. **Client** — Login with Client tab: enter an email that exists as a client; check that email for the magic link. Open the link, then use Report and Ask.
4. **Resend** — For real email (magic link, reports, reply-to), use an API key from the Resend account where your domain is verified (see `.env.example` comments).

## 6. Test reply-to-email (simulated)

The real flow: user replies to a report email → Resend receives it → Resend POSTs to your API → API answers and sends a reply email.

To test **without** sending a real email, use the test endpoint. It uses the same logic but takes `from_email`, `subject`, and `text` in the request body (no Resend `email_id` needed).

**Prereqs:** A client with that email exists and has at least one report. `RESEND_API_KEY` and `OPENAI_API_KEY` must be set so the API can generate the answer and send the reply.

**PowerShell:**

```powershell
cd c:\Users\cwstg\shopping-agent-real\fullnoise\fullnoise-api
.\.venv\Scripts\Activate.ps1
# Then from another terminal, or after ensuring API is running:
.\scripts\test-reply-to-email.ps1 -FromEmail "client@example.com" -Question "Why did costs go up?"
```

**curl:**

```powershell
curl -X POST http://localhost:8000/webhooks/resend/inbound-test -H "Content-Type: application/json" -d "{\"from_email\":\"client@example.com\",\"subject\":\"Report\",\"text\":\"Why did costs go up?\"}"
```

- Success: `{"ok":true,"message":"reply sent"}` — check the client’s inbox for the reply.
- No client: `{"ok":false,"error":"no client with that email"}` (404).
- Empty text: `{"ok":false,"error":"text is required"}` (400).

**Real reply-to-email:** In Resend, set the inbound webhook URL to `https://your-api-url/webhooks/resend/inbound`. When someone replies to a report email, Resend will POST there with `type: "email.received"` and `data.email_id`; the API fetches the email from Resend and runs the same answer-and-reply logic.

---

## Quick API checks (with API running)

```powershell
# Health
curl http://localhost:8000/health

# Contact (no auth)
curl -X POST http://localhost:8000/contact -H "Content-Type: application/json" -d "{\"name\":\"Test\",\"email\":\"test@example.com\",\"message\":\"Hi\"}"
```
