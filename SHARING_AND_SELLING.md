# Sharing the agent for testing & selling it

## Sales platform (website to sell the agent)

A **sales website** is in the **`sales-platform`** folder. It includes:

- **Landing page** — hero, features, “Buy now” with your price
- **Stripe Checkout** — customers pay by card; you get the money in Stripe
- **Success page** — after payment, the customer gets a **Download** button (your zip link). The link is only shown after Stripe confirms payment.

**To use it:** Open `sales-platform/README.md` and follow the steps: create a Stripe product and price, set your download URL (e.g. Google Drive link to your zip), add env variables, then run locally with `npm install` and `npm run dev` or deploy to Vercel. When you deploy and set `NEXT_PUBLIC_BASE_URL` and `DOWNLOAD_URL`, you can share the site link and start selling.

---

## Sending the agent to someone to test

### What to send (and what not to)

**Include:**
- All `.py` files: `agent.py`, `planner.py`, `memory.py`, `price_compare.py`, `coles_tool.py`, `woolies_tool.py`
- `config.json` (or a fresh copy – see below)
- `requirements.txt`
- `START_HERE.md`
- `Run agent.bat` (optional; nice for Windows testers)

**Do not include:**
- The `.venv` folder (huge; they create their own)
- `profile.json` (your preferences/memory – they get their own)
- `cart.json` (session data)
- `run_logs/` (your run history)

### Easy way: create a “share” zip

1. In File Explorer, go to `c:\Users\cwstg\shopping-agent-real`.
2. Select only: `agent.py`, `planner.py`, `memory.py`, `price_compare.py`, `coles_tool.py`, `woolies_tool.py`, `config.json`, `requirements.txt`, `START_HERE.md`, `Run agent.bat`.
3. Right‑click → **Send to** → **Compressed (zipped) folder**. Name it e.g. `shopping-agent-v1.zip`.

Send that zip (email, Google Drive, Dropbox, etc.). The tester unzips it, follows **START_HERE.md**, and runs the agent. They use their own Woolworths/Coles login in the browser when prompted.

### Optional: clean config for testers

Your `config.json` has your defaults (people, days, budget). You can either:
- Leave it as is (testers can edit the numbers), or
- Add a `config.example.json` with neutral defaults and tell testers to rename it to `config.json` if they want a fresh start.

---

## Making money: ways to sell the agent

### 1. Sell the zip (one‑time purchase)

- **Where:** Gumroad, Payhip, or your own site + Stripe/PayPal.
- **How:** Buyer pays → you send the zip (or they get an automatic download link).
- **Pros:** Simple, you keep full control of the code.
- **Cons:** No automatic updates unless you email new versions; some people may share the zip.

### 2. License key (optional layer)

- You add a small check in `agent.py`: at startup, read a `license.txt` or ask for a key; if missing/invalid, print a message and a link to buy.
- Keys can be simple (e.g. name + short code you generate). For real “unlock” you’d host a tiny server or use a service (e.g. Gumroad license checks, Paddle, etc.).
- **Pros:** Lets you sell “licensed” copies and (if you want) revoke or limit sharing.
- **Cons:** Extra code and possibly a backend; determined users can bypass.

### 3. Subscription / membership

- **Where:** Patreon, Gumroad membership, or a private GitHub repo + payment.
- **How:** Pay monthly/annually → access to the latest zip (or repo). You release updates and only members get them.
- **Pros:** Recurring revenue, incentive to keep improving.
- **Cons:** You need to deliver updates and support.

### 4. “Pay what you want” or tip jar

- Put the agent on Gumroad (or similar) as “free download” with an optional payment. Good for validation and early feedback before you set a fixed price.

---

## Practical next steps

1. **Validate:** Send the zip to 2–3 people (friends or a small Facebook/Reddit group for Aussie grocery shoppers). Ask them to follow START_HERE.md and report what broke or felt confusing.
2. **Fix and simplify:** Use their feedback to fix bugs and maybe shorten START_HERE or add a one‑page “Quick start.”
3. **Then sell:** Put the improved zip on Gumroad (or similar) with a clear description: “Automated meal planning + Woolworths/Coles cart builder for Windows. You run it locally; you stay logged in and in control.”
4. **Price idea:** Start low (e.g. one‑time $5–15 or “pay what you want”) to get buyers and reviews; raise later if demand is there.

---

## Legal / terms (when selling)

- Add a short **LICENSE** or **Terms**: “For personal use only; no resale or redistribution of the code.”
- Clarify you’re not affiliated with Woolworths or Coles; the agent only automates the browser like a user would.
- If you’re in Australia and earn over the threshold, consider GST and tax/accounting.

---

## Summary

| Goal                    | Action |
|-------------------------|--------|
| Let someone test it     | Zip the code + START_HERE (no .venv, no profile/cart/run_logs); send zip. |
| Sell it one‑time        | Put the same zip on Gumroad/Payhip; buyer downloads after payment. |
| Sell with updates       | Use a membership (Patreon/Gumroad) and send new zips to paying members. |
| Slightly protect copies | Add a simple license check and sell “licensed” zips; optional. |

Once testers confirm it works on their machine, you can start selling the same (or improved) package with confidence.
