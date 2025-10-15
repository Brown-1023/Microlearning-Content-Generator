@echo off
echo Starting Microlearning Content Generator
echo ========================================
echo.

REM Start backend
echo Starting backend server...
start /B python run.py

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
)

REM Start frontend
echo Starting frontend...
cd frontend
start /B npm run dev
cd ..

echo.
echo ========================================
echo Application started successfully!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:4000
echo.
echo Press Ctrl+C to stop both servers
pause
