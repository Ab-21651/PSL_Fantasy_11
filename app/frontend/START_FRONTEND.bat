@echo off
echo ========================================
echo    CricMind Frontend - Quick Start
echo ========================================
echo.

cd /d "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"

echo Checking for package.json...
if not exist package.json (
    echo ERROR: package.json not found!
    echo Please run this script from the frontend directory.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
echo (This may take 2-3 minutes on first run)
echo.

if exist node_modules (
    echo Dependencies already installed. Skipping...
) else (
    echo Running: npm install
    call npm install
    if errorlevel 1 (
        echo.
        echo ERROR: npm install failed!
        echo Make sure Node.js is installed: https://nodejs.org/
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Starting Frontend Dev Server...
echo ========================================
echo.
echo Frontend will open at: http://localhost:5173
echo.
echo IMPORTANT: Make sure your backend is running at http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

call npm run dev
