# Autonomous Shopping Agent

A **full autonomous agent** that does your grocery shopping: it plans meals from recipes, builds a cart, and can **compare prices between Coles and Woolworths** and ask you whether to choose the cheaper option. It fills one or both carts in the browser; you pay manually at checkout.

## Flow: Plan → Compare (optional) → Act → Observe → Learn

1. **Plan** – Uses your config (or prompts) to pick recipes and build an ingredient list.
2. **Compare** – Optionally fetches prices at Woolworths and Coles; for each item where one store is cheaper, asks: *“Use [store] (cheaper) for this item? (Y/n)”*. Builds a split cart (Woolworths + Coles).
3. **Act** – Opens Woolworths and/or Coles and adds items to each cart via browser automation.
4. **Observe** – Records what was added and what failed.
5. **Learn** – Saves failures and preferences to your profile for next time.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
playwright install chromium
```

## Modes

### Interactive (default)

Prompts for people, days, budget, foods to avoid, and recipe picks. Asks **“Compare prices at Coles and Woolworths? (y/n)”**; if you say yes, it fetches prices and for each item where one store is cheaper, asks whether to use the cheaper option. Then asks for approval and fills one or both carts.

```bash
python agent.py
```

### Autonomous

Uses `config.json` for people, days, budget, avoid list, and recipe selection. No prompts except optional approval.

```bash
# Use config; still asks "Type 'approve' to fill cart"
python agent.py --auto

# Full autonomy: no approval prompt, fill cart immediately
python agent.py --auto --approve

# Test without opening browser
python agent.py --auto --dry-run
```

### Config

Edit `config.json`:

```json
{
  "autonomous": {
    "people": 2,
    "days": 5,
    "budget": 140.0,
    "avoid": ["nuts"],
    "recipe_picks": "all",
    "compare_prices": false,
    "auto_approve": false,
    "dry_run": false,
    "headless": false
  }
}
```

- `recipe_picks`: `"all"` or comma-separated numbers, e.g. `"1,3,5"`.
- `compare_prices`: if `true`, in autonomous mode compares Coles vs Woolworths and asks you to choose the cheaper option per item (same as saying “y” in interactive).
- `auto_approve`: if `true`, no approval prompt (same as `--approve`).
- `dry_run`: simulate only (no browser).
- `headless`: run browser in the background.

## Files

| File           | Purpose |
|----------------|--------|
| `agent.py`     | Main entry: interactive or autonomous loop. |
| `memory.py`    | Load/save `profile.json` (preferences, substitutions). |
| `planner.py`   | Recipes, meal plan, and cart building. |
| `woolies_tool.py` | Woolworths: search, get price, add to cart. |
| `coles_tool.py`   | Coles: search, get price, add to cart. |
| `price_compare.py`| Compares cart prices across stores and asks client to choose cheaper. |
| `config.json`  | Defaults for autonomous mode. |
| `profile.json` | Created on first run; your preferences and learnings. |
| `run_logs/`    | One JSON log per run. |

## Adding recipes

Edit `planner.py`: add entries to the `RECIPES` dict with `name`, `serves`, and `ingredients` (list of `(name, qty_per_serve)`).

## Security

- The agent **never** handles payment. It only adds items to the cart; you complete checkout and pay on Woolworths and/or Coles.
- Keep `profile.json` and `config.json` local; they can contain preferences and avoid lists.

## Optional: run without Playwright

If you don’t install Playwright, `woolies_tool` runs in dry-run mode: it reports what it would add without opening a browser.
