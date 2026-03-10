@echo off
REM Run the Boss Assistant in automated mode (no prompts).
REM Schedule this .bat with Windows Task Scheduler to run the report by itself.
cd /d "%~dp0"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo No .venv found. Run: python -m venv .venv then pip install -r requirements.txt
    exit /b 1
)
python run_automated.py
exit /b %ERRORLEVEL%
