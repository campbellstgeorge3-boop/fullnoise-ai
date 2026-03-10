# Resend reply-to-email setup

When a client **replies** to their FullNoise report email, Resend receives the email and POSTs to your API. The API looks up the client, answers the question using their latest report, and sends a reply email back.

## 1. Resend dashboard (same account as your domain)

1. Log in at [resend.com](https://resend.com) with the **same account** where your domain is verified (e.g. campbellstgeorge3@gmail.com).
2. Go to **Inbound** (or **Receiving** / **Webhooks** depending on the UI).
3. Add an **Inbound Webhook** (or “Webhook URL” for received emails).
4. Set the URL to your **public** API base + path:
   ```text
   https://YOUR-API-HOST/webhooks/resend/inbound
   ```
   Examples:
   - Production: `https://fullnoise-api.railway.app/webhooks/resend/inbound`
   - Ngrok (local test): `https://abc123.ngrok.io/webhooks/resend/inbound`
5. Save. Resend will send `POST` requests with `Content-Type: application/json` and body:
   ```json
   { "type": "email.received", "data": { "email_id": "..." } }
   ```

## 2. API environment

In your API `.env` (or production env vars):

- **RESEND_API_KEY** — API key from **this same Resend account** (the one with the domain and the webhook).
- **RESEND_FROM_EMAIL** — Sender address on your **verified domain** (e.g. `reports@yourdomain.com`). Replies will be sent from this address.
- **OPENAI_API_KEY** — Used to generate the answer from the report context.

## 3. What has to exist in your app

- The **sender’s email** (the “From” of the reply) must exist as a **Client** in your DB with that exact email.
- That client must have at least one **Report**. The reply is based on their latest report.

If there’s no matching client, the webhook still returns `200 OK` (so Resend doesn’t retry) but no reply is sent.

## 4. How to test

**Real reply (end-to-end):**

1. Send a report to a client (Admin → Send report, or use the worker).
2. In your mail client, **reply** to that report email and ask something (e.g. “Why did costs go up?”).
3. Resend receives the reply, calls your webhook, and your API should send an answer back to the client’s email.
4. Check **Resend → Logs** (same account) to see the inbound event and the outbound reply.

**Simulated (no real email):**

If your API is running (e.g. locally or on a public URL), you can hit the test endpoint so the same “answer + send reply” logic runs without Resend inbound:

```powershell
curl -X POST https://YOUR-API-HOST/webhooks/resend/inbound-test -H "Content-Type: application/json" -d "{\"from_email\":\"client@example.com\",\"subject\":\"Report\",\"text\":\"Why did costs go up?\"}"
```

Use a `from_email` that is a client in your DB and has a report. You should get `{"ok":true,"message":"reply sent"}` and the reply email at that address.

## 5. Troubleshooting

- **No reply email**
  - Confirm the webhook URL in Resend is exactly `https://YOUR-API-HOST/webhooks/resend/inbound` (no trailing slash).
  - Confirm **RESEND_API_KEY** is from the same Resend account that has the domain and the webhook.
  - Check API logs for `inbound webhook error:` (the handler logs and still returns 200).
  - In Resend, check **Logs** for the inbound event and any errors.

- **“No API keys” / no logs under your email**
  - You’re likely using an API key from a **different** Resend account. Create a key in the account where the domain is verified and set that as **RESEND_API_KEY**.

- **Replies not threading**
  - The real webhook sends `In-Reply-To` when Resend provides `message_id`. If threading still fails, check that your **RESEND_FROM_EMAIL** is on the same domain as the original report.
