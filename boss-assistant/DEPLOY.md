# How to make the Boss Assistant website live

Your app **is** the website (landing page + dashboard + client portal). To make it a real site on the internet, deploy it to a host.

**Included in this project:**
- `Procfile` — for Railway, Heroku, or any host that uses it (run command)
- `Dockerfile` + `.dockerignore` — for Docker-based deploy (Railway, Fly.io, etc.)
- `render.yaml` — for Render.com (optional blueprint)
- `requirements.txt` — includes FastAPI and uvicorn

Push to GitHub, connect the repo to a host, add env vars, and deploy.

---

## Option 1: Railway (recommended)

### 1. Put your code on GitHub

1. Create a **GitHub** account if you don’t have one: https://github.com
2. Create a **new repository** (e.g. `boss-assistant`). Don’t add a README yet.
3. On your PC, open PowerShell in the **parent** of `boss-assistant` (e.g. `shopping-agent-real`), or in `boss-assistant` if the project is only that folder.
4. If you’re in `boss-assistant`, run:

   ```powershell
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/boss-assistant.git
   git push -u origin main
   ```

   **Important:** Make sure `.env`, `tokens/`, `client_tokens.json` are in `.gitignore` (they are) so you never push secrets.

### 2. Deploy on Railway

1. Go to **https://railway.app** and sign in (e.g. with GitHub).
2. Click **New Project** → **Deploy from GitHub repo**.
3. Choose your **boss-assistant** repo. Railway will detect the app.
4. Set the **root directory** to the folder that contains `chat_server.py` (e.g. `boss-assistant` if the repo is the whole repo and that’s the app folder).
5. **Environment variables** (in Railway project → Variables): add the same ones as in your `.env`:

   - `OPENAI_API_KEY`
   - `RESEND_API_KEY`
   - `REPORT_EMAIL_FROM`
   - `SESSION_SECRET` (long random string, for client portal)
   - Optional: `CONTACT_EMAIL_TO`, `DASHBOARD_PASSWORD`

6. **Start command:** Railway often auto-detects. If not, set:

   ```bash
   uvicorn chat_server:app --host 0.0.0.0 --port $PORT
   ```

7. **Deploy.** Railway will build and run the app and give you a URL like `https://boss-assistant-production-xxxx.up.railway.app`.

### 3. Use your URL as the website

- **Landing page:** `https://your-railway-url.up.railway.app/`
- **Dashboard:** `https://your-railway-url.up.railway.app/dashboard`
- **Client sign in:** `https://your-railway-url.up.railway.app/client/login`

### 4. Resend webhook (for reply-by-email)

In **Resend** → your domain → **Receiving / Webhooks**, set:

```text
https://your-railway-url.up.railway.app/api/inbound-email
```

Replace `your-railway-url` with your real Railway URL.

### 5. (Optional) Custom domain

In Railway: Project → **Settings** → **Domains** → add e.g. `app.fullnoises.com`. Railway will show what CNAME to set at your domain registrar. Point that CNAME to the value they give. Then use `https://app.fullnoises.com` as your website and webhook URL.

---

## Option 2: Render

1. Go to **https://render.com**, sign in (e.g. with GitHub).
2. **New** → **Web Service** → connect your **boss-assistant** repo.
3. **Root directory:** `boss-assistant` (if your repo has the app in that subfolder).
4. **Runtime:** Python 3.
5. **Build command:** `pip install -r requirements.txt` (or leave default if it detects it).
6. **Start command:** `uvicorn chat_server:app --host 0.0.0.0 --port $PORT`
7. **Environment:** Add the same variables as in `.env` (see list above).
8. **Deploy.** Render gives you a URL like `https://boss-assistant-xxxx.onrender.com`.

Then use that URL as your website and set the Resend webhook to `https://your-render-url.onrender.com/api/inbound-email`.

---

## Checklist before you deploy

- [ ] `.env` is **not** in the repo (it’s in `.gitignore`).
- [ ] `tokens/` and `client_tokens.json` are in `.gitignore`.
- [ ] **requirements.txt** is in the app folder (it includes `fastapi`, `uvicorn`).
- [ ] If the repo has the app in a subfolder (e.g. `boss-assistant`), set that as **root directory** on the host.
- [ ] **clients.json**: On the server, paths (e.g. `csv_path`) must be valid for Linux. Use relative paths and include the CSV in the repo, or configure clients after deploy via env/file.

---

## After deploy

- Share the **landing URL** with prospects.
- Use **dashboard** to send reports.
- Clients use **Client sign in** or reply to report emails.
- Set **CONTACT_EMAIL_TO** so the contact form sends leads to your email.

That’s how the “website” is made: same app, running on Railway or Render instead of your PC.
