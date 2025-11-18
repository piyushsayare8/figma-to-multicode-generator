@echo off
echo ========================================
echo   Starting FULL PROJECT
echo   Backend + Frontend
echo ========================================
echo.

REM Start backend in a new window
start "Backend Server" cmd /k "cd /d "%~dp0backend" && START_BACKEND.bat"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in a new window
start "Frontend Server" cmd /k "cd /d "%~dp0frontend" && START_FRONTEND.bat"

echo.
echo ========================================
echo Both servers are starting...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo Close the terminal windows to stop servers
echo ========================================
echo.

pause
