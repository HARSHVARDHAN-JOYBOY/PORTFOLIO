@echo off
title Portfolio Server
color 0B
echo.
echo  ============================================
echo   PORTFOLIO SERVER - Starting...
echo  ============================================
echo.
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Download: https://www.python.org/downloads/
    echo  IMPORTANT: Tick "Add Python to PATH" during install
    pause & exit /b
)
echo  [1/2] Installing packages...
pip install flask flask-cors werkzeug --quiet
echo  [2/2] Starting server...
echo.
echo  Open browser: http://localhost:5000
echo  Admin panel:  click the gear icon in footer
echo  Password:     admin@123
echo.
echo  Press Ctrl+C to stop
echo  ============================================
echo.
python app.py
pause
