@echo off
cd /d "c:\Users\cwstg\shopping-agent-real"
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
)
python agent.py
pause
