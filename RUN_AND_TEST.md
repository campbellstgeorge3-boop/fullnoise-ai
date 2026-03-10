# How to Run and Test the Shopping Agent

Follow these steps to set up, run, and test the agent safely.

---

## 1. One-time setup

Open a terminal in the project folder (`shopping-agent-real`).

### Create a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Install the browser (for real cart filling)

```powershell
playwright install chromium
```

You can skip this step if you only want to test with **dry-run** (no browser).

---

## 2. Test without opening a browser (dry-run)

This checks that planning and cart building work. **No browser opens and no store is touched.**

```powershell
python agent.py --auto --dry-run
```

You should see:
- Your meal plan and cart list
- A line like `-> Woolworths: 38 items   Coles: 0 items`
- `(Test run - no browser used.)`
- A run log path, e.g. `run_logs\run_20260219_123456.json`

If that runs without errors, the agent pipeline is working.

---

## 3. Interactive mode (with prompts)

Best for everyday use: the agent asks you questions, then you choose whether to add to cart.

```powershell
python agent.py
```

You will be asked:
1. How many people, days, budget, foods to avoid
2. Which recipes (e.g. `1,3,5` or `all`)
3. Whether to compare Coles vs Woolworths (y/n)
4. Whether to add items to your online cart (yes/no)

If you say **no** at the last step, nothing is added and no browser opens.  
If you say **yes**, a browser opens and the agent fills Woolworths (and Coles if you used price comparison).

---

## 4. Autonomous mode (uses config.json)

Uses settings from `config.json` so you don’t have to type them each time.

```powershell
# Asks once: "Add these to your online cart? (yes/no)" then runs
python agent.py --auto

# No approval prompt; fills cart as soon as the plan is ready (use with care)
python agent.py --auto --approve
```

To test without opening a browser:

```powershell
python agent.py --auto --dry-run
```

---

## 5. Quick test checklist

| Step | Command | What it checks |
|------|---------|-----------------|
| 1 | `python agent.py --auto --dry-run` | Plan + cart build, no browser |
| 2 | `python agent.py` then answer prompts and say **no** at "Add to cart?" | Interactive flow, no cart fill |
| 3 | `python agent.py` then say **yes** at "Add to cart?" | Real browser, Woolworths cart filled |
| 4 | Same as 3 but say **y** to "Compare Coles vs Woolworths?" | Price comparison + optional Coles cart |

---

## 6. Where things are saved

- **profile.json** – Your preferences and learned substitutions (created on first run).
- **config.json** – Defaults for `--auto` (people, days, budget, compare_prices, etc.).
- **cart.json** – Last built cart (written before filling).
- **run_logs/** – One JSON file per run (plan, cart, results).

---

## 7. Troubleshooting

- **"playwright not found" or browser errors**  
  Run: `playwright install chromium`

- **Unicode/encoding errors on Windows**  
  Use a terminal that supports UTF-8, or the agent will fall back to ASCII (e.g. `->` instead of arrows).

- **Nothing happens when I say yes**  
  Make sure Chromium is installed and no other program is blocking the browser.

- **I want to change defaults**  
  Edit `config.json` for autonomous mode, or edit `profile.json` for things like default people/days and substitutions.
