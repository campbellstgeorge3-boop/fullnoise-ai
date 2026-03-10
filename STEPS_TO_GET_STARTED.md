# Step-by-step: Get the shopping agent underway

Do these in order. Check off each step when you're done.

---

## Step 1: Open the project folder in a terminal

1. Open **PowerShell** (or Command Prompt).
2. Go to your project folder. For example:
   ```powershell
   cd c:\Users\cwstg\shopping-agent-real
   ```
3. Confirm you're in the right place: you should see files like `agent.py`, `config.json`, `requirements.txt` in this folder.

**Done when:** Your terminal prompt shows you're inside `shopping-agent-real`.

---

## Step 2: Create a virtual environment

Run this **one** command:

```powershell
python -m venv .venv
```

**Done when:** The command finishes with no error. You may see nothing printed — that's OK. A folder named `.venv` will appear in your project.

---

## Step 3: Turn on the virtual environment

Run this **one** command:

```powershell
.venv\Scripts\Activate.ps1
```

- If you use **Command Prompt** instead of PowerShell, use:
  ```cmd
  .venv\Scripts\activate.bat
  ```

**Done when:** Your terminal prompt starts with `(.venv)` — for example:
`(.venv) PS C:\Users\cwstg\shopping-agent-real>`

---

## Step 4: Install Python dependencies

Run:

```powershell
pip install -r requirements.txt
```

**Done when:** You see something like "Successfully installed playwright-..." with no red error messages.

---

## Step 5: Install the browser (for real cart filling later)

Run:

```powershell
playwright install chromium
```

This downloads Chromium so the agent can open a browser when you say "yes" to adding items to your cart.

**Done when:** The command finishes and says it installed Chromium (or that it's already installed).

---

## Step 6: Test the agent without opening a browser (dry-run)

Run:

```powershell
python agent.py --auto --dry-run
```

**Done when:** You see:
- A meal plan (list of recipes)
- A cart list (ingredients and quantities)
- A line like: `-> Woolworths: 38 items   Coles: 0 items`
- The message: `(Test run - no browser used.)`
- A path like: `Run log: run_logs\run_YYYYMMDD_HHMMSS.json`

No browser should open. If you see all of that, the agent is working.

---

## Step 7: Run the agent interactively (with questions)

Run:

```powershell
python agent.py
```

You will be asked:
1. **How many people are you shopping for?** — Type a number or press Enter for 2.
2. **Meal plan for how many days?** — Type a number or press Enter for 5.
3. **What's your budget in dollars?** — Type a number or press Enter for 140.
4. **Any ingredients to avoid?** — Type things like `nuts, dairy` or press Enter to skip.
5. **Your choice (e.g. 1,3,5 or all):** — Type `all` or numbers like `1,3,5` for recipes.
6. **Compare Coles vs Woolworths...? (y/N)** — Type `n` or press Enter to skip for now.
7. **Add these to your online cart? (yes/no)** — Type **no** for this test so no browser opens.

**Done when:** The agent finishes and says something like "No problem. Come back whenever you're ready." You've now seen the full interactive flow without filling a real cart.

---

## Step 8 (optional): Fill a real cart

When you're ready for the agent to open a browser and add items to Woolworths:

1. Run again: `python agent.py`
2. Answer the questions (or use defaults with Enter).
3. When asked **"Add these to your online cart? (yes/no)"** — type **yes**.
4. A browser window will open; the agent will search and add items. You complete checkout and payment yourself on the Woolworths site.

**Done when:** You've seen the browser open and items added (or you've run it once and are comfortable with the flow).

---

## Summary checklist

| # | What to do | Command or action |
|---|------------|--------------------|
| 1 | Open terminal in project folder | `cd c:\Users\cwstg\shopping-agent-real` |
| 2 | Create virtual environment | `python -m venv .venv` |
| 3 | Activate it | `.venv\Scripts\Activate.ps1` |
| 4 | Install dependencies | `pip install -r requirements.txt` |
| 5 | Install browser | `playwright install chromium` |
| 6 | Test without browser | `python agent.py --auto --dry-run` |
| 7 | Run with questions (say "no" to cart) | `python agent.py` |
| 8 | (Optional) Fill real cart (say "yes") | `python agent.py` then yes at the end |

After Step 6, you're "underway" — the agent runs and you can use it. Steps 7 and 8 get you used to the prompts and real cart filling.
