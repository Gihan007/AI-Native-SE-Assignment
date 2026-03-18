@echo off
REM AI-Powered Website Audit Tool - Setup & Run Script for Windows

echo.
echo ============================================
echo AI-Powered Website Audit Tool Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [1/4] Checking Python installation...
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [2/4] Creating virtual environment...
    python -m venv venv
) else (
    echo [2/4] Virtual environment already exists
)

REM Activate virtual environment
echo [3/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo [4/4] Installing dependencies...
pip install -r backend\requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo ============================================
    echo ⚠️  IMPORTANT: Configure your environment
    echo ============================================
    echo.
    echo 1. Copy .env.example to .env
    echo 2. Add your OpenAI API key to .env
    echo.
    echo Steps:
    echo   - Set OPENAI_API_KEY=your_api_key_here
    echo.
    echo You can get an API key at: https://platform.openai.com/api-keys
    echo.
)

echo.
echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo To start the application:
echo   1. Make sure you have configured .env with your OpenAI API key
echo   2. Run: python backend/main.py
echo   3. Open browser to: http://localhost:8000
echo.
echo To serve the frontend:
echo   - Copy frontend/ files to a web server, or
echo   - Use 'python -m http.server 3000' in the frontend/ directory
echo.
pause
