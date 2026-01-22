@echo off
echo ========================================
echo   Starting ScrapeAll System
echo ========================================

echo 1. Starting Backend Server...
start "ScrapeAll Backend" cmd /k "call start_backend.bat"

echo 2. Waiting for backend to initialize...
timeout /t 5

echo 3. Starting Frontend...
start "ScrapeAll Frontend" cmd /k "call start_frontend.bat"

echo.
echo ========================================
echo   System Started!
echo ========================================
echo Backend running in new window
echo Frontend running in new window
echo.
echo Access the app at: http://localhost:3000 (or 3001/3002 if 3000 is busy)
pause
