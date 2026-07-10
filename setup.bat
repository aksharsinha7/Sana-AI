@echo off
echo === AI Teacher Setup ===
echo.

echo [1/3] Setting up Python backend...
cd backend
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo.

echo [2/3] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo Created .env - please add your ANTHROPIC_API_KEY to backend\.env
) else (
    echo .env already exists, skipping.
)
cd ..

echo [3/3] Installing frontend dependencies...
cd frontend
npm install
cd ..

echo.
echo === Setup complete! ===
echo.
echo Next steps:
echo   1. Add your Anthropic API key to backend\.env
echo   2. Run start.bat to launch the app
echo.
pause
