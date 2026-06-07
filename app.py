"""
╔══════════════════════════════════════════════════════╗
║         PORTFOLIO BACKEND — Flask + SQLite           ║
║   Your data lives on the SERVER, not the browser!   ║
╚══════════════════════════════════════════════════════╝

HOW TO RUN:
  1. Install deps:   pip install flask flask-cors
  2. Start server:   python app.py
  3. Open browser:   http://localhost:5000
  4. Share on LAN:   http://<your-ip>:5000
  5. Admin panel:    Click ⚙ icon → password: admin@123
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import os

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'portfolio.db')

# ─── Default Portfolio Data ────────────────────────────────────────────────────
DEFAULT_DATA = {
    "pw": "admin@123",
    "profile": {
        "firstName": "YOUR",
        "lastName": "NAME",
        "bioShort": "Passionate MCA Student building the future, one line of code at a time.",
        "bio": "I'm a passionate MCA student with a strong foundation in programming and web development. I love building innovative solutions that solve real-world problems.",
        "roles": ["MCA Student", "Python Developer", "Flask Developer", "C++ Programmer", "Prompt Engineer", "Problem Solver"],
        "avatar": ""
    },
    "skills": [
        {"id": 1,  "name": "Python",                "level": 85, "category": "Programming"},
        {"id": 2,  "name": "Flask",                 "level": 75, "category": "Framework"},
        {"id": 3,  "name": "C++",                   "level": 70, "category": "Programming"},
        {"id": 4,  "name": "SQL",                   "level": 80, "category": "Database"},
        {"id": 5,  "name": "HTML",                  "level": 90, "category": "Web"},
        {"id": 6,  "name": "CSS",                   "level": 85, "category": "Web"},
        {"id": 7,  "name": "Prompt Engineering",    "level": 88, "category": "AI"},
        {"id": 8,  "name": "Presentation",          "level": 82, "category": "Soft Skills"},
        {"id": 9,  "name": "Team Leadership",       "level": 85, "category": "Soft Skills"},
        {"id": 10, "name": "Communication",         "level": 80, "category": "Soft Skills"}
    ],
    "projects": [
        {
            "id": 1,
            "title": "Student Management System",
            "description": "A full-featured web application built with Python and Flask for managing student records, grades, and attendance with a robust SQL database backend.",
            "tags": ["Python", "Flask", "SQL", "HTML/CSS"],
            "link": "#",
            "github": "#"
        },
        {
            "id": 2,
            "title": "AI Prompt Toolkit",
            "description": "A comprehensive collection of optimized prompts and templates for various AI use cases, demonstrating advanced prompt engineering techniques for productivity.",
            "tags": ["Prompt Engineering", "AI", "Python"],
            "link": "#",
            "github": "#"
        }
    ],
    "achievements": [
        {"id": 1, "title": "Academic Excellence",  "description": "Consistently ranked in top 10% of class throughout MCA program", "year": "2024", "icon": "🏆"},
        {"id": 2, "title": "Hackathon Finalist",   "description": "Reached finals in college-level coding competition with Flask solution", "year": "2024", "icon": "⚡"}
    ],
    "gallery": [],
    "contact": {
        "email": "your.email@example.com",
        "phone": "+91 XXXXXXXXXX",
        "location": "India",
        "github": "#",
        "linkedin": "#",
        "twitter": "#",
        "instagram": "#"
    },
    "cv": None
}


# ─── Database Helpers ──────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables and seed with default data if empty."""
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id   INTEGER PRIMARY KEY,
                data TEXT    NOT NULL
            )
        ''')
        row = conn.execute('SELECT id FROM portfolio WHERE id = 1').fetchone()
        if not row:
            conn.execute('INSERT INTO portfolio (id, data) VALUES (1, ?)',
                         [json.dumps(DEFAULT_DATA)])
        conn.commit()
    print("✅  Database ready:", DB_PATH)


def read_portfolio():
    """Read portfolio data from DB, fall back to defaults."""
    with get_db() as conn:
        row = conn.execute('SELECT data FROM portfolio WHERE id = 1').fetchone()
        if row:
            return json.loads(row['data'])
    return json.loads(json.dumps(DEFAULT_DATA))


def write_portfolio(data: dict):
    """Persist portfolio data to DB."""
    with get_db() as conn:
        conn.execute('UPDATE portfolio SET data = ? WHERE id = 1',
                     [json.dumps(data)])
        conn.commit()


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route('/')
def index():
    """Serve the portfolio HTML."""
    return render_template('index.html')


@app.route('/api/data', methods=['GET'])
def api_get_data():
    """
    Return all portfolio data (except the password).
    Everyone who opens the portfolio calls this automatically.
    """
    data = read_portfolio()
    # Never send the password to the browser
    safe = {k: v for k, v in data.items() if k != 'pw'}
    return jsonify(safe)


@app.route('/api/verify-pw', methods=['POST'])
def api_verify_pw():
    """
    Admin login: check if the submitted password is correct.
    Returns { valid: true } or 403.
    """
    body = request.get_json(silent=True) or {}
    pw = body.get('pw', '')
    stored = read_portfolio()
    if pw == stored.get('pw', 'admin@123'):
        return jsonify({'valid': True})
    return jsonify({'valid': False, 'error': 'Wrong password'}), 403


@app.route('/api/save', methods=['POST'])
def api_save():
    """
    Save updated portfolio data.
    Request body: { pw: "...", data: { ...portfolio... } }
    The submitted password must match the stored one.
    """
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'error': 'No JSON body received'}), 400

    submitted_pw = body.get('pw', '')
    new_data     = body.get('data', {})

    # ── Auth check ──────────────────────────────────────────────────
    stored = read_portfolio()
    if submitted_pw != stored.get('pw', 'admin@123'):
        return jsonify({'error': 'Invalid password — save rejected'}), 403

    # ── Merge & persist ─────────────────────────────────────────────
    stored.update(new_data)
    # Allow password change only if a new 'pw' key is in the payload
    if 'pw' in new_data and new_data['pw']:
        stored['pw'] = new_data['pw']

    write_portfolio(stored)
    return jsonify({'success': True, 'message': 'Portfolio saved!'})


@app.route('/api/reset', methods=['POST'])
def api_reset():
    """Reset portfolio to factory defaults (requires password)."""
    body = request.get_json(silent=True) or {}
    stored = read_portfolio()
    if body.get('pw', '') != stored.get('pw', 'admin@123'):
        return jsonify({'error': 'Invalid password'}), 403

    write_portfolio(DEFAULT_DATA)
    return jsonify({'success': True, 'message': 'Portfolio reset to defaults'})


# ─── Dev Entry Point ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("─" * 55)
    print("🚀  Portfolio server starting…")
    print("   Local:    http://localhost:5000")
    print("   Network:  http://0.0.0.0:5000")
    print("   Admin pw: admin@123  (change it after first login!)")
    print("─" * 55)
    # host='0.0.0.0' makes the server reachable from other devices
    # on the same Wi-Fi network
    app.run(host='0.0.0.0', port=5000, debug=False)
