@echo off
echo Starting AI Teacher...
echo.

start "AI Teacher Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate && uvicorn main:app --reload --port 8001"
timeout /t 2 /nobreak >nul
start "AI Teacher Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo App is starting!
echo   Backend:  http://localhost:8001
echo   Frontend: http://localhost:5173
echo.
timeout /t 3 /nobreak >nul
start http://localhost:5173
