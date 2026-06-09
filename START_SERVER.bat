@echo off
title Portfolio Server (Aiven MySQL)
color 0B
echo.
echo  ============================================
echo   PORTFOLIO SERVER — Aiven MySQL Mode
echo  ============================================
echo.
echo  IMPORTANT: Set these in a .env file or system variables:
echo    MYSQL_HOST     = your-aiven-host.aivencloud.com
echo    MYSQL_PORT     = 12546
echo    MYSQL_USER     = avnadmin
echo    MYSQL_PASSWORD = your-password
echo    MYSQL_DATABASE = defaultdb
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Download from python.org
    pause & exit /b
)

echo [1/2] Installing packages...
pip install flask flask-cors werkzeug PyMySQL cryptography --quiet

echo [2/2] Starting server...
echo.
echo  Open: http://localhost:5000
echo  Admin: click gear icon in footer
echo  Password: admin@123
echo  Press Ctrl+C to stop
echo  ============================================
echo.
python app.py
pause
