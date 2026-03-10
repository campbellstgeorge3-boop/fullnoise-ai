@echo off
cd /d "%~dp0"
:: Start the app (small window + server in background). No need to keep this window open.
start "" ".venv\Scripts\pythonw.exe" run_app.py
