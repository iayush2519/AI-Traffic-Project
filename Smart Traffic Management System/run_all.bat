@echo off
echo Starting AI Traffic Management System...

:: Start the Python backend using uv
echo [1/2] Starting FastAPI Backend on Port 8000...
start cmd /k "cd backend && uv run python run.py"

:: Wait a moment for backend to initialize
timeout /t 3 > nul

:: Start the React frontend
echo [2/2] Starting React Frontend on Port 5173...
start cmd /k "cd frontend && npm run dev"

echo Both services launched in new terminal windows!
echo Access the Dashboard at: http://localhost:5173
echo Access the API Docs at: http://127.0.0.1:8000/docs
pause
