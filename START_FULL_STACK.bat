@echo off
echo ========================================
echo    CricMind - Start Full Stack App
echo ========================================
echo.
echo This will start:
echo   1. Backend API (http://localhost:8000)
echo   2. Frontend App (http://localhost:5173)
echo.
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo ========================================
echo   Step 1: Starting Backend API...
echo ========================================
echo.

cd /d "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"

start "CricMind Backend" cmd /k "uvicorn app.main:app --reload"

timeout /t 3 > nul

echo.
echo ========================================
echo   Step 2: Starting Frontend...
echo ========================================
echo.

cd /d "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

start "CricMind Frontend" cmd /k "npm run dev"

timeout /t 5 > nul

echo.
echo ========================================
echo   ✅ BOTH SERVERS STARTED!
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo   Docs: http://localhost:8000/docs
echo.
echo Frontend App: http://localhost:5173
echo.
echo Two command windows opened:
echo   1. Backend (keep this open)
echo   2. Frontend (keep this open)
echo.
echo Close those windows to stop the servers.
echo.
echo Opening frontend in browser...
echo ========================================
echo.

timeout /t 3 > nul
start http://localhost:5173

echo.
echo Press any key to close this window...
pause > nul
