@echo off
title Cloud Storage Management System - Launcher
echo ============================================================
echo   Cloud Storage Management System - Starting Server...
echo ============================================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not found in PATH. Please install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if .env exists, if not copy from .env.example
if not exist .env (
    echo [INFO] Creating .env file from .env.example...
    copy .env.example .env
)

REM Install or verify dependencies
echo [INFO] Verifying dependencies...
pip install -r requirements.txt --quiet

echo.
echo ============================================================
echo   Starting Cloud Storage Application on http://127.0.0.1:5000
echo   Press CTRL+C in this window to stop the server.
echo ============================================================
echo.

python app.py

pause
