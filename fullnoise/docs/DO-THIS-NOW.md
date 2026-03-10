# Exactly what to do

Do these in order. One step = one action.

---

## Before you start

Your FullNoise code must be on **GitHub**. If the folder `shopping-agent-real` (or `fullnoise`) is not in a GitHub repo yet:

1. Go to https://github.com and sign in.
2. Click the **+** (top right) → **New repository**.
3. Name it anything (e.g. `fullnoise`). Don’t add a README. Create.
4. On your PC, open PowerShell in your project folder and run (replace YOUR_USERNAME and REPO_NAME with yours):

   cd c:\Users\cwstg\shopping-agent-real
   git init
   git add .
   git commit -m "fullnoise"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
   git push -u origin main

5. Then come back here and start from Step 1 below.

---

## RAILWAY

**1.** Open: https://railway.app  

**2.** Sign in with GitHub.

**3.** Click **New Project**.

**4.** Click **Deploy from GitHub repo**.

**5.** Select your repo. Wait until the first deploy finishes.

**6.** Click **+ New** → **Database** → **PostgreSQL**. Wait until it’s ready.

**7.** Click **+ New** → **Database** → **Redis**. Wait until it’s ready.

**8.** Click the **PostgreSQL** service (not your app). Open the **Variables** tab. Copy the value of **DATABASE_URL** (the long line starting with `postgresql://`). Paste it in Notepad. At the start, change `postgresql://` to `postgresql+asyncpg://`. Copy that new line. You’ll use it in step 15.

**9.** Click the **Redis** service. Open **Variables**. Copy **REDIS_URL**. Keep it for step 15.

**10.** Click your **app service** (the one with your repo name). Click **Settings**.

**11.** Find **Root Directory**. Set it to exactly:
```
fullnoise/fullnoise-api
```

**12.** Find **Start Command** or **Deploy** → **Start Command**. Set it to exactly:
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**13.** Click **Variables** for this same app service.

**14.** Click **+ New Variable** (or **Add variable**). Add these 9 variables. For each: first box = Name, second box = Value.

- Name: `DATABASE_URL`  
  Value: the line from step 8 (starts with `postgresql+asyncpg://`)

- Name: `REDIS_URL`  
  Value: the value from step 9

- Name: `NEXTAUTH_SECRET`  
  Value: `hti+utj17snjXRxQIESIcJEEm55kGS66riBTYs6dXSY=`

- Name: `OPENAI_API_KEY`  
  Value: your OpenAI key (starts with `sk-`)

- Name: `RESEND_API_KEY`  
  Value: your Resend key (starts with `re_`)

- Name: `RESEND_FROM_EMAIL`  
  Value: the email you send from (e.g. `reports@yourdomain.com`)

- Name: `FRONTEND_URL`  
  Value: `https://temp.vercel.app`

- Name: `ADMIN_EMAIL`  
  Value: `admin@fullnoise.ai`

- Name: `ADMIN_PASSWORD`  
  Value: `admin`

**15.** In the same app service, open **Settings** → **Networking** (or **Generate domain**). Click **Generate domain**. Copy the URL it shows (e.g. `https://xxxx.up.railway.app`). This is your **API URL**. Save it in Notepad.

**16.** Back on the project, click **+ New** → **GitHub Repo** → same repo.

**17.** Click the new service. **Settings** → **Root Directory**: `fullnoise/fullnoise-api`

**18.** **Start Command**: `arq app.worker.WorkerSettings`

**19.** **Variables**: add the same 9 variables as in step 14 (same names, same values). No domain needed.

---

## VERCEL

**20.** Open: https://vercel.com  

**21.** Sign in with GitHub.

**22.** Click **Add New** → **Project**.

**23.** Select your repo. Click **Import**.

**24.** Before deploying: **Root Directory** → **Edit** → type: `fullnoise/fullnoise-web`

**25.** **Environment Variables**. Add 3:

- Name: `NEXT_PUBLIC_API_URL`  
  Value: paste your **API URL** from step 15 (no slash at the end)

- Name: `NEXTAUTH_SECRET`  
  Value: `hti+utj17snjXRxQIESIcJEEm55kGS66riBTYs6dXSY=`

- Name: `NEXTAUTH_URL`  
  Value: leave empty for now

**26.** Click **Deploy**. Wait until it’s done.

**27.** Copy the URL Vercel gives you (e.g. `https://xxx.vercel.app`). This is your **Vercel URL**. Save it.

**28.** Vercel project → **Settings** → **Environment Variables**. Add or edit: Name `NEXTAUTH_URL`, Value = your **Vercel URL**. Save.

**29.** Railway → your **app service** (not the worker) → **Variables**. Change `FRONTEND_URL` to your **Vercel URL** (from step 27). Save.

---

## RESEND

**30.** Open: https://resend.com and sign in.

**31.** Go to **Inbound** (or **Webhooks** / **Receiving**).

**32.** Set **Webhook URL** to (use your API URL from step 15):
```
https://YOUR-API-URL-HERE/webhooks/resend/inbound
```
Example: if API URL is `https://fullnoise.up.railway.app`, then:
```
https://fullnoise.up.railway.app/webhooks/resend/inbound
```
Save.

---

## TEST

**33.** In the browser open your **Vercel URL**.

**34.** Click **Sign in** → **Admin** tab. Email: `admin@fullnoise.ai`  Password: `admin`

**35.** You should see the admin page. Add a client with your email (if there’s an Add button). Click **Send report** for that client.

**36.** Check your email for the report. Reply to it with a question. You should get a reply back.

---

If you get stuck, say the step number and what you see on the screen.
