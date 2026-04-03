@echo off
echo ========================================
echo    Fixing Frontend Dependencies
echo ========================================
echo.

cd /d "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"

echo Deleting old node_modules and lock files...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
if exist bun.lock del bun.lock

echo.
echo Installing fresh dependencies...
echo (This will take 2-3 minutes)
echo.

call npm install

if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    echo Make sure Node.js is installed: https://nodejs.org/
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✅ Dependencies Fixed!
echo ========================================
echo.
echo You can now run: npm run dev
echo.
pause
