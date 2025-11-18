@echo off
echo ========================================
echo   Starting Figma to Multicode Backend
echo ========================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    echo.
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Install/upgrade dependencies
echo Installing dependencies...
pip install --quiet --upgrade pip
pip install --quiet uvicorn fastapi python-multipart pillow opencv-python numpy
echo.

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.
python -m uvicorn app_new:app --reload --host 0.0.0.0 --port 8000

pause
