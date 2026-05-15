@echo off
echo ========================================================
echo Starting Antigravity Insight-to-Action Showcase...
echo ========================================================
echo.

echo [1/2] Launching FastAPI Backend (Port 8000)...
start "Antigravity Backend" cmd /k "cd apps\backend && echo Installing dependencies... && pip install -r requirements.txt && echo Starting Server... && uvicorn app.main:app --reload --port 8000"

echo [2/2] Launching Next.js Frontend (Port 3000)...
start "Antigravity Web Dashboard" cmd /k "cd apps\frontend-web && echo Installing dependencies... && npm install && echo Starting Server... && npm run dev"

echo.
echo All services are spinning up in separate windows!
echo Waiting for servers to initialize before opening browser...
timeout /t 10
start http://localhost:3000

echo Done! You can close this window.
exit
