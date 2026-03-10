@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting Boss Assistant (landing + dashboard + reply-by-email). Keep this window open.
echo.
echo Landing:  http://localhost:8001/
echo Dashboard: http://localhost:8001/dashboard
echo.
start "" "http://localhost:8001/"
uvicorn chat_server:app --host 0.0.0.0 --port 8001
