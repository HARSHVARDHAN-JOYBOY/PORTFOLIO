#!/bin/bash
echo ""
echo "============================================"
echo "  PORTFOLIO SERVER - Starting..."
echo "============================================"
echo ""
pip3 install flask flask-cors werkzeug --quiet
echo "Open browser: http://localhost:5000"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
[ -n "$IP" ] && echo "Network:      http://$IP:5000"
echo "Admin panel:  click gear icon in footer"
echo "Password:     admin@123"
echo "Press Ctrl+C to stop"
echo "============================================"
echo ""
python3 app.py
