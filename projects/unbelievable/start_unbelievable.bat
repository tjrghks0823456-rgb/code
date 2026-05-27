@echo off
title Unbelievable Launcher

echo Starting Backend (FastAPI)...
start "Unbelievable Backend" cmd /k "cd /d "%~dp0backend" && call venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

echo Starting Frontend (Next.js)...
start "Unbelievable Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Opening Browser...
timeout /t 5 /nobreak >nul
start http://localhost:3500
start http://localhost:3000
exit
