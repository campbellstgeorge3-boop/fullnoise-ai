# Reply to email — do this now

Get automatic email replies when someone replies to the report. Follow these steps in order.

---

## Step 1: Start the reply server

Open **PowerShell** in the boss-assistant folder:

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\activate
uvicorn chat_server:app --host 0.0.0.0 --port 8001
```

Leave this window **open**. If you see "Application startup complete", the server is running.

(Using port **8001** avoids "port already in use" if something else is on 8000.)

---

## Step 2: Expose it with ngrok

Open a **second** PowerShell window:

```powershell
ngrok http 8001
```

Copy the **https** URL (e.g. `https://abc123.ngrok-free.app`). Leave this window open.

---

## Step 3: Add the webhook in Resend

1. Go to **https://resend.com/webhooks**
2. Click **Add** (or **Create webhook**)
3. **Endpoint URL:** paste your ngrok URL + `/api/inbound-email`  
   Example: `https://abc123.ngrok-free.app/api/inbound-email`
4. **Events:** turn on **email.received**
5. Save

---

## Step 4: Send a report (so you have an email to reply to)

In a **third** PowerShell:

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\activate
python main.py --run-client default
```

Check your inbox — you should get the report from `reports@mail.fullnoises.com` (or the fallback address if the domain isn’t verified yet).

---

## Step 5: Reply and get an answer

1. Open that report email
2. Click **Reply**
3. Type a question, e.g. **What was my profit?** or **Send my report again**
4. Send

You should get an automatic reply by email within a short time.

---

## If it doesn’t work

- **Server and ngrok** must both be running when you reply (Steps 1 and 2).
- The report must be sent **from** an address that receives mail (e.g. `reports@mail.fullnoises.com`) so your reply goes to Resend and triggers the webhook. If you only send from `onboarding@resend.dev`, replies may not hit your webhook.
- In Resend → Webhooks, check for failed deliveries or errors on your endpoint.
- If you use a **new ngrok URL**, update the webhook URL in Resend to match.
