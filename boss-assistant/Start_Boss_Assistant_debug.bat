@echo off
cd /d "%~dp0"
echo Starting Boss Assistant (debug - this window stays open)...
echo.
call .venv\Scripts\activate.bat
python run_app.py
echo.
echo Exited. Press any key to close.
pause >nul
