@echo off
title Portfolio Server
echo ============================================
echo   Installing dependencies...
echo ============================================
pip install flask flask-cors

echo.
echo ============================================
echo   Starting your Portfolio Server...
echo ============================================
echo.
echo   Open in browser:  http://localhost:5000
echo   Share on network: http://YOUR-IP:5000
echo   Admin password:   admin@123
echo.
echo   Press Ctrl+C to stop the server
echo ============================================
echo.

python app.py

pause
