@echo off
cd /d %~dp0
set PLAYWRIGHT_BROWSERS_PATH=%CD%\.playwright-browsers
if not exist .venv (
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app:app --reload
pause
