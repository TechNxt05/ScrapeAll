@echo off
echo ========================================
echo   ScrapeAll - Quick Start Script
echo ========================================
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.9+
    pause
    exit /b 1
)
echo.

echo Step 2: Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.

echo Step 3: Installing Playwright browsers...
playwright install chromium
echo.

echo Step 4: Checking environment variables...
cd ..
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env file with your API keys
    echo See README.md for instructions
    pause
)
echo.

echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Add your API keys to .env file (at least GROQ_API_KEY)
echo 2. Run: start_backend.bat
echo 3. Open: frontend-simple\index.html in your browser
echo.
pause
