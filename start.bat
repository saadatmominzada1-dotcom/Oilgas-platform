@echo off
echo.
echo Starting OilGas Intelligence Platform...
echo.

:: Start backend using venv python.exe directly
start "OilGas Backend" cmd /k "cd backend && venv\Scripts\python.exe main.py"

:: Wait a moment for backend to initialize
timeout /t 5 /nobreak >nul

:: Start frontend
start "OilGas Frontend" cmd /k "cd frontend && npm start"

echo.
echo ==============================================
echo   Platform starting!
echo   Open: http://localhost:3000
echo   (Two terminal windows opened)
echo ==============================================
echo.
pause
