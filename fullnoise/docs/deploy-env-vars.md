# Deploy — env vars checklist

Copy these variable **names** into Railway (API + worker) and fill in the values. Use the same `NEXTAUTH_SECRET` on Vercel.

## Railway API & Worker (same for both)

| Variable | Where to get it |
|----------|------------------|
| `DATABASE_URL` | Railway Postgres service → copy URL → change `postgresql://` to `postgresql+asyncpg://` |
| `REDIS_URL` | Railway Redis service → copy connection URL |
| `NEXTAUTH_SECRET` | You create one (32+ chars). Same value on Vercel. |
| `OPENAI_API_KEY` | Your OpenAI API key (platform.openai.com) |
| `RESEND_API_KEY` | Resend dashboard → API Keys (same account as your domain) |
| `RESEND_FROM_EMAIL` | Your verified sender, e.g. `reports@yourdomain.com` |
| `FRONTEND_URL` | Your Vercel URL, e.g. `https://your-project.vercel.app` (set after Vercel deploy) |
| `ADMIN_EMAIL` | Email you’ll use to sign in as admin |
| `ADMIN_PASSWORD` | Password for admin sign-in |

## Vercel (fullnoise-web)

| Variable | Value |
|----------|--------|
| `NEXT_PUBLIC_API_URL` | Your Railway API URL, e.g. `https://xxx.up.railway.app` |
| `NEXTAUTH_SECRET` | Same as Railway `NEXTAUTH_SECRET` |
| `NEXTAUTH_URL` | Your Vercel URL, e.g. `https://your-project.vercel.app` |

## Generate NEXTAUTH_SECRET (PowerShell)

Run once and paste the result into Railway and Vercel:

```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Maximum 256 }) -as [byte[]])
```
