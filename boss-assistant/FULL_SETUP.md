# Full setup (no shortcuts)

Proper setup so everything works: your domain for sending and receiving, reports from reports@mail.fullnoises.com, and reply-by-email.

---

## 1. Domain in Resend (sending + receiving)

Go to https://resend.com/domains and open **mail.fullnoises.com**.

You need **both**:
- **Enable Sending** – DKIM and SPF **Verified**
- **Enable Receiving** – MX for `mail` **Verified**

**In Cloudflare (DNS for fullnoises.com):**

- Type: TXT | Name: `resend._domainkey.mail` | Content: (DKIM from Resend)
- Type: MX | Name: `send.mail` | Target: `feedback-smtp.us-east-1.amazonses.com.` | Priority: 10
- Type: TXT | Name: `send.mail` | Content: `v=spf1 include:amazonses.com ~all`
- Type: MX | Name: `mail` | Target: `inbound-smtp.us-east-1.amazonaws.com.` | Priority: 10

Proxy: **DNS only** (grey cloud) on all. Use a **trailing dot** on MX targets.

Wait 10–15 min, then in Resend click Verify. If either Sending or Receiving stays Pending, fix the DNS Resend shows and verify again.

Check: `nslookup -type=mx mail.fullnoises.com` should show inbound-smtp.us-east-1.amazonaws.com.

---

## 2. .env

In boss-assistant\.env:

```
REPORT_EMAIL_FROM=reports@mail.fullnoises.com
```

No spaces around `=`. Plus OPENAI_API_KEY and RESEND_API_KEY.

---

## 3. Send report

```powershell
cd c:\Users\cwstg\shopping-agent-real\boss-assistant
.venv\Scripts\activate
python main.py --run-client default
```

If you see "domain is not verified", Step 1 is not done. When it sends with no error, the report is from your domain.

---

## 4. Reply-by-email

**4a.** Start server: `uvicorn chat_server:app --host 0.0.0.0 --port 8000` (leave running).

**4b.** Start ngrok: `ngrok http 8000` (leave running). Copy the https URL.

**4c.** Resend → Webhooks → Add. Endpoint: `https://YOUR-NGROK-URL/api/inbound-email`. Event: **email.received**. Save.

**4d.** Send a report, reply to it with a question; you should get an automatic reply by email.

---

## Checklist

- [ ] Resend: mail.fullnoises.com – Enable Sending = Verified
- [ ] Resend: mail.fullnoises.com – Enable Receiving = Verified
- [ ] Cloudflare: all 4 records; DNS only; trailing dot on MX
- [ ] .env: REPORT_EMAIL_FROM=reports@mail.fullnoises.com
- [ ] python main.py --run-client default sends (no domain error)
- [ ] Server + ngrok running; webhook added in Resend
- [ ] Reply to report email → automatic reply received

When all are checked, the full setup is in place.
