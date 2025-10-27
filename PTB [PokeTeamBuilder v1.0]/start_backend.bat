@echo off
REM Pokemon Team Builder - Start Backend Server
REM This script starts the backend server for email verification and API services

echo ============================================================
echo Pokemon Team Builder - Backend Server
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

REM Check if Flask is installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask flask-cors
    echo.
)

REM Start the backend server
echo Starting backend server...
echo.
python start_backend.py

pause
