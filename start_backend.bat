@echo off
echo ========================================
echo   Starting ScrapeAll Backend
echo ========================================
echo.
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

REM Run from the project root to ensure imports work correctly
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
