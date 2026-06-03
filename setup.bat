@echo off
echo.
echo ==============================================
echo   OilGas Intelligence Platform - Setup
echo ==============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from https://python.org
    pause & exit /b 1
)
echo [OK] Python found

:: Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Install Node.js 18+ from https://nodejs.org
    pause & exit /b 1
)
echo [OK] Node.js found

:: Backend setup
echo.
echo Setting up backend...
cd backend
python -m venv venv

:: Use venv's own python.exe to upgrade pip — avoids global pip path confusion
echo    Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip -q

:: Install dependencies via venv pip directly
echo    Installing dependencies (this may take a few minutes)...
venv\Scripts\pip.exe install -r requirements.txt -q
echo [OK] Backend dependencies installed

if not exist .env (
    copy .env.example .env
    echo [OK] Created backend\.env
)
cd ..

:: Frontend setup
echo.
echo Setting up frontend...
cd frontend
npm install --legacy-peer-deps --silent
echo [OK] Frontend dependencies installed
cd ..

echo.
echo ==============================================
echo   Setup complete!
echo ==============================================
echo.
echo To start: double-click start.bat
echo.
echo Optional - edit backend\.env to add:
echo   ANTHROPIC_API_KEY  = AI-powered summaries
echo   TELEGRAM_BOT_TOKEN = Telegram delivery
echo   GNEWS_API_KEY      = Extra news sources
echo.
pause
