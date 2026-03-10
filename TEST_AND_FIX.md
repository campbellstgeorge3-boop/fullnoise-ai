# Test the Shopping Agent and Run Until It Works

## Quick test (no browser)

```powershell
python test_agent.py
```

- **Exit 0** = agent dry-run completed and printed plan + cart.
- **Exit 1** = something failed (see printed output).

## Run once and exit with pass/fail

```powershell
python run_until_working.py
```

Same as `python test_agent.py` but with a clear "Tests passed" or "Tests failed" message.

## Retry several times (e.g. after fixes)

```powershell
python run_until_working.py --loop 5
```

Runs the test up to 5 times. Exits 0 as soon as one run passes.

## Use an agent to fix until perfect

1. Run the test: `python run_until_working.py`
2. If it fails, fix the code (or ask Cursor to fix it using the error output).
3. Run again: `python run_until_working.py`
4. Repeat until exit code is 0.

In Cursor you can say: *"Run run_until_working.py in shopping-agent-real. If it fails, fix the shopping agent and run it again until it passes."* The agent will run the script, read failures, edit the code, and re-run until the test passes.

## What the test checks

- `agent.py --auto --dry-run` runs to completion (exit 0).
- Output contains "Your plan", "Your cart", and "Dry run" (no browser is opened).

No store sites are hit and no browser is launched.
