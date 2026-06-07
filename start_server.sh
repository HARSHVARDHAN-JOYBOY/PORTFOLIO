#!/bin/bash
echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║        PORTFOLIO SERVER — STARTING           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "[1/3] Installing dependencies..."
pip3 install flask flask-cors werkzeug --quiet
echo "[2/3] Dependencies ready."
echo "[3/3] Starting server..."
echo ""
echo "┌──────────────────────────────────────────────┐"
echo "│  Local:   http://localhost:5000              │"
IP=$(hostname -I 2>/dev/null | awk '{print $1}')
echo "│  Network: http://$IP:5000        │"
echo "│  Admin:   click ⚙ in footer                │"
echo "│  Password: admin@123                        │"
echo "│  Press Ctrl+C to stop                       │"
echo "└──────────────────────────────────────────────┘"
echo ""
python3 app.py
