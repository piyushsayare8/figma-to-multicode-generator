@echo off
REM Efficiently start backend and frontend, then open browser

REM Start backend in new window with ILS v2 architecture
start "Backend" cmd /c "cd backend && .venv\Scripts\activate && uvicorn app:app --reload --host 127.0.0.1 --port 8000"

REM Start frontend in new window
start "Frontend" cmd /c "cd frontend && npm run dev"

REM Wait a few seconds for servers to start
ping 127.0.0.1 -n 5 >nul

REM Open the main UI page in default browser
start http://localhost:5173
