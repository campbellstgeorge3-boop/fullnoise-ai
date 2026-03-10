# Start Here – Shopping Agent

> **"Can't open file 'agent.py'"** — You're in the wrong folder. Open PowerShell, go to **this folder** (where you unzipped the agent), then run `python agent.py`. Or double‑click **Run agent.bat**.

Plan meals from **30+ recipes**, get one grocery list, then add items to your **Woolworths** or **Coles** cart. Super simple: one prompt (or press Enter), review your list, then we fill the cart. **We never see or store your password** — you log in in the browser once; we remember your session for next time.

---

## What you need

- **This folder** (where `agent.py` and `START_HERE.md` live)
- **PowerShell** — Press Windows key, type `powershell`, press Enter

---

## One-time setup (do this once)

### 1. Open PowerShell and go to this folder

```
cd path\to\this\folder
```

(Replace with the real path, e.g. `cd C:\Users\YourName\Downloads\shopping-agent-real`.)  
You must be in the folder that contains `agent.py`.

### 2. Create and activate the virtual environment

```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

You should see **(.venv)** at the start of the line.

### 3. Install dependencies and browser

```
pip install -r requirements.txt
playwright install chromium
```

Wait until both finish.

### 4. Quick test (no browser, no cart)

```
python agent.py --auto --dry-run
```

You should see a meal plan and a grocery list. If so, setup is done.

---

## Running the agent

```
python agent.py
```

1. **People, days, budget** — Type e.g. `2 5 140` (2 people, 5 days, $140) or just **Enter** for defaults (2 people, 5 days, $140).
2. **Anything to avoid?** — e.g. nuts, shellfish, or **Enter** to skip.
3. **Recipes** — Type numbers (e.g. `1,3,7`), or **all**, or just **Enter** for a quick mix of 8 recipes.
4. **Review your list** — Remove any item by typing its number (e.g. `2,5`) or **Enter** to keep all.
5. **Best basket / compare?** — Only asked if Coles is enabled in `config.json`. Otherwise we add everything to Woolworths.
6. **Add to cart?** — Say **yes**; a browser opens. If you're not logged in, **log in on the website** (we never see your password). Then press **Enter** in the terminal. We add the items. Next time you run, you may already be logged in.

You pay at checkout on the store site. We never add more than 20 items in one run.

---

## Login & safety

- The agent opens the **Woolworths or Coles website** in a browser. It does **not** log in for you with a stored password.
- **First time:** When the browser opens, log in on the site as you normally would. Set your delivery/pickup location if asked. Then press Enter in the terminal so we can add items.
- **Next times:** We use a saved browser profile (cookies/session). You may already be logged in; if not, log in again in the browser.
- **We never see, store, or send your password.** Everything stays in your browser.

---

## If something goes wrong

- **"python is not recognized"** — Install Python from python.org (latest 3.x), then run the setup again from step 1.
- **(.venv) doesn't appear** — Close PowerShell, open it again, `cd` to this folder, run `.venv\Scripts\Activate.ps1` again.
- **Wrong folder?** — In PowerShell, type `dir`. You should see `agent.py`, `requirements.txt`, `START_HERE.md`.
- **Coles** — Coles is **off by default** (it often blocks automated browsers). The agent uses Woolworths only unless you turn Coles on: in `config.json` set `"coles_enabled": true`, or add `"coles_enabled": true` to your profile. If Coles still shows "content is blocked", keep it off and add Coles items manually at coles.com.au using `cart.json`.

---

## Super short version

1. `cd` to this folder → `python -m venv .venv` → `.venv\Scripts\Activate.ps1` → `pip install -r requirements.txt` → `playwright install chromium`
2. `python agent.py --auto --dry-run` to test.
3. `python agent.py` to run — Enter for quick defaults, then follow the prompts.
