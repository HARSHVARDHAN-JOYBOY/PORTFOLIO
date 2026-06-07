@echo off
title Portfolio Server — Flask
color 0B
echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║        PORTFOLIO SERVER — STARTING           ║
echo  ╚══════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python not found!
    echo  Download from: https://www.python.org/downloads/
    echo  Make sure to check "Add Python to PATH" during install.
    pause
    exit /b
)

echo  [1/3] Python found.

:: Install dependencies
echo  [2/3] Installing dependencies...
pip install flask flask-cors werkzeug --quiet
if %errorlevel% neq 0 (
    echo  [ERROR] Failed to install packages.
    pause
    exit /b
)
echo  [2/3] Dependencies ready.

:: Start server
echo  [3/3] Starting server...
echo.
echo  ┌──────────────────────────────────────────────┐
echo  │  Local:   http://localhost:5000              │
echo  │  Network: http://YOUR-IP:5000               │
echo  │  Admin:   click ⚙ in footer                │
echo  │  Password: admin@123                        │
echo  │                                              │
echo  │  Press Ctrl+C to stop the server            │
echo  └──────────────────────────────────────────────┘
echo.
python app.py
pause
