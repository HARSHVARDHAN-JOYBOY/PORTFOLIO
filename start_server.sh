#!/bin/bash
echo "============================================"
echo "  Installing dependencies..."
echo "============================================"
pip install flask flask-cors

echo ""
echo "============================================"
echo "  Starting your Portfolio Server..."
echo "============================================"
echo ""
echo "  Open in browser:  http://localhost:5000"
echo "  Share on network: http://$(hostname -I | awk '{print $1}'):5000"
echo "  Admin password:   admin@123"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "============================================"
echo ""

python3 app.py
