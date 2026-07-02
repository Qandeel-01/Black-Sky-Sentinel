@echo off
echo Starting Black Sky - Southern Punjab Risk Index
echo.

echo [1/2] Starting Flask backend on http://localhost:5000
start "Black Sky Backend" cmd /k "cd /d %~dp0backend && .venv\Scripts\python app.py"

timeout /t 2 /nobreak >nul

echo [2/2] Starting React frontend on http://localhost:5173
start "Black Sky Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo Both servers started. Open http://localhost:5173 in your browser.
