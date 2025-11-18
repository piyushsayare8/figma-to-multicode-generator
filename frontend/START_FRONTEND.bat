@echo off
echo ========================================
echo   Starting Figma to Multicode Frontend
echo ========================================
echo.

cd /d "%~dp0"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
    echo.
)

REM Start the frontend dev server
echo Starting frontend dev server...
echo.
echo Frontend will open at http://localhost:5173
echo Press Ctrl+C to stop the server
echo ========================================
echo.
call npm run dev

pause
