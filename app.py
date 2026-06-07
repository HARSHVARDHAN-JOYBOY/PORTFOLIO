"""
╔══════════════════════════════════════════════════════════╗
║         PORTFOLIO BACKEND  —  Flask + SQLite             ║
║                                                          ║
║  Tables:  portfolio  → stores all portfolio JSON         ║
║           messages   → contact form messages (CRUD)      ║
║                                                          ║
║  Uploads: /uploads/  → real files (photos, CV, gallery)  ║
╚══════════════════════════════════════════════════════════╝
"""

from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import sqlite3, json, os, uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# ── App setup ─────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder='templates')
CORS(app)

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
DB_PATH      = os.path.join(BASE_DIR, 'portfolio.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_IMAGES = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
ALLOWED_DOCS   = {'pdf', 'doc', 'docx'}
MAX_IMG_SIZE   = 5  * 1024 * 1024   # 5 MB
MAX_DOC_SIZE   = 10 * 1024 * 1024   # 10 MB

# ── Default portfolio data ─────────────────────────────────────────────────────
DEFAULT = {
    "pw": "admin@123",
    "profile": {
        "firstName": "YOUR", "lastName": "NAME",
        "bioShort": "Passionate MCA Student building the future, one line of code at a time.",
        "bio": "I'm a passionate MCA student with a strong foundation in programming and web development. I love building innovative solutions that solve real-world problems.",
        "roles": ["MCA Student","Python Developer","Flask Developer","C++ Programmer","Prompt Engineer","Problem Solver"],
        "avatar": ""
    },
    "skills": [
        {"id":1,  "name":"Python",             "level":85, "category":"Programming"},
        {"id":2,  "name":"Flask",              "level":75, "category":"Framework"},
        {"id":3,  "name":"C++",               "level":70, "category":"Programming"},
        {"id":4,  "name":"SQL",               "level":80, "category":"Database"},
        {"id":5,  "name":"HTML",              "level":90, "category":"Web"},
        {"id":6,  "name":"CSS",              "level":85, "category":"Web"},
        {"id":7,  "name":"Prompt Engineering","level":88, "category":"AI"},
        {"id":8,  "name":"Presentation",      "level":82, "category":"Soft Skills"},
        {"id":9,  "name":"Team Leadership",   "level":85, "category":"Soft Skills"},
        {"id":10, "name":"Communication",     "level":80, "category":"Soft Skills"},
    ],
    "projects": [
        {"id":1,"title":"Student Management System",
         "description":"A full-featured web application built with Python and Flask for managing student records, grades, and attendance with a robust SQL database backend.",
         "tags":["Python","Flask","SQL","HTML/CSS"],"link":"#","github":"#"},
        {"id":2,"title":"AI Prompt Toolkit",
         "description":"A comprehensive collection of optimized prompts and templates for various AI use cases, demonstrating advanced prompt engineering techniques.",
         "tags":["Prompt Engineering","AI","Python"],"link":"#","github":"#"},
    ],
    "achievements": [
        {"id":1,"title":"Academic Excellence","description":"Consistently ranked in top 10% of class throughout MCA program","year":"2024","icon":"🏆"},
        {"id":2,"title":"Hackathon Finalist","description":"Reached finals in college-level coding competition with Flask solution","year":"2024","icon":"⚡"},
    ],
    "gallery": [],
    "contact": {
        "email":"your.email@example.com","phone":"+91 XXXXXXXXXX","location":"India",
        "github":"#","linkedin":"#","twitter":"#","instagram":"#"
    },
    "cv": None
}

# ── Database helpers ───────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Portfolio data table (single JSON row)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id   INTEGER PRIMARY KEY,
                data TEXT    NOT NULL
            )""")
        # Contact messages table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL,
                subject    TEXT    DEFAULT '',
                message    TEXT    NOT NULL,
                is_read    INTEGER DEFAULT 0,
                created_at TEXT    DEFAULT (datetime('now','localtime'))
            )""")
        # Seed default data if first run
        if not conn.execute('SELECT id FROM portfolio WHERE id=1').fetchone():
            conn.execute('INSERT INTO portfolio VALUES (1,?)', [json.dumps(DEFAULT)])
        conn.commit()
    print("✅  Database ready:", DB_PATH)

def read_portfolio():
    with get_db() as conn:
        row = conn.execute('SELECT data FROM portfolio WHERE id=1').fetchone()
        return json.loads(row['data']) if row else json.loads(json.dumps(DEFAULT))

def write_portfolio(data: dict):
    with get_db() as conn:
        conn.execute('UPDATE portfolio SET data=? WHERE id=1', [json.dumps(data)])
        conn.commit()

def verify_pw(submitted: str) -> tuple:
    """Returns (stored_data, ok:bool)"""
    stored = read_portfolio()
    return stored, submitted == stored.get('pw', 'admin@123')

def allowed_file(filename: str, allowed: set) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed

def save_upload(file, prefix='file') -> str:
    """Save an uploaded file and return its public URL path."""
    ext = secure_filename(file.filename).rsplit('.', 1)[1].lower()
    filename = f"{prefix}_{uuid.uuid4().hex[:10]}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    return f'/uploads/{filename}'


# ══════════════════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ── Health check ───────────────────────────────────────────────────────────────
@app.route('/api/ping')
def api_ping():
    unread = 0
    try:
        with get_db() as conn:
            unread = conn.execute('SELECT COUNT(*) FROM messages WHERE is_read=0').fetchone()[0]
    except Exception: pass
    return jsonify({
        'status':  'ok',
        'python':  __import__('sys').version.split()[0],
        'db':      os.path.exists(DB_PATH),
        'unread':  unread,
        'time':    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

# ── Portfolio data ─────────────────────────────────────────────────────────────
@app.route('/api/data')
def api_get():
    data = read_portfolio()
    data.pop('pw', None)   # never send password to browser
    return jsonify(data)

@app.route('/api/verify-pw', methods=['POST'])
def api_verify():
    body = request.get_json(silent=True) or {}
    stored, ok = verify_pw(body.get('pw', ''))
    if ok:
        with get_db() as conn:
            unread = conn.execute('SELECT COUNT(*) FROM messages WHERE is_read=0').fetchone()[0]
        return jsonify({'valid': True, 'unread': unread})
    return jsonify({'valid': False, 'error': 'Wrong password'}), 403

@app.route('/api/save', methods=['POST'])
def api_save():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({'error': 'No data received'}), 400
    stored, ok = verify_pw(body.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    new = body.get('data', {})
    stored.update(new)
    if new.get('pw'):
        stored['pw'] = new['pw']
    write_portfolio(stored)
    return jsonify({'success': True})

@app.route('/api/reset', methods=['POST'])
def api_reset():
    body = request.get_json(silent=True) or {}
    _, ok = verify_pw(body.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    write_portfolio(json.loads(json.dumps(DEFAULT)))
    return jsonify({'success': True})

# ── File uploads ───────────────────────────────────────────────────────────────
@app.route('/api/upload/avatar', methods=['POST'])
def upload_avatar():
    stored, ok = verify_pw(request.form.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    if not allowed_file(f.filename, ALLOWED_IMAGES):
        return jsonify({'error': 'Only JPG, PNG, GIF, WEBP allowed'}), 400
    if request.content_length and request.content_length > MAX_IMG_SIZE:
        return jsonify({'error': 'Max 5MB allowed'}), 400
    # Delete old avatar file if it was an upload
    old = stored.get('profile', {}).get('avatar', '')
    if old.startswith('/uploads/'):
        old_path = os.path.join(UPLOAD_FOLDER, os.path.basename(old))
        if os.path.exists(old_path):
            os.remove(old_path)
    url = save_upload(f, prefix='avatar')
    stored['profile']['avatar'] = url
    write_portfolio(stored)
    return jsonify({'success': True, 'url': url})

@app.route('/api/upload/gallery', methods=['POST'])
def upload_gallery():
    stored, ok = verify_pw(request.form.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    if not allowed_file(f.filename, ALLOWED_IMAGES):
        return jsonify({'error': 'Only image files allowed'}), 400
    caption = request.form.get('caption', '')
    url = save_upload(f, prefix='gallery')
    item = {'id': uuid.uuid4().hex, 'url': url, 'caption': caption}
    stored.setdefault('gallery', []).append(item)
    write_portfolio(stored)
    return jsonify({'success': True, 'item': item})

@app.route('/api/upload/cv', methods=['POST'])
def upload_cv():
    stored, ok = verify_pw(request.form.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    f = request.files['file']
    if not allowed_file(f.filename, ALLOWED_DOCS):
        return jsonify({'error': 'Only PDF, DOC, DOCX allowed'}), 400
    # Remove old CV
    old = (stored.get('cv') or {}).get('url', '')
    if old.startswith('/uploads/'):
        old_path = os.path.join(UPLOAD_FOLDER, os.path.basename(old))
        if os.path.exists(old_path):
            os.remove(old_path)
    url = save_upload(f, prefix='cv')
    cv_data = {'url': url, 'name': secure_filename(f.filename)}
    stored['cv'] = cv_data
    write_portfolio(stored)
    return jsonify({'success': True, 'cv': cv_data})

@app.route('/api/delete/gallery-item', methods=['POST'])
def delete_gallery_item():
    body = request.get_json(silent=True) or {}
    stored, ok = verify_pw(body.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403
    item_id = body.get('id')
    gallery = stored.get('gallery', [])
    item = next((g for g in gallery if g['id'] == item_id), None)
    if item and item['url'].startswith('/uploads/'):
        path = os.path.join(UPLOAD_FOLDER, os.path.basename(item['url']))
        if os.path.exists(path):
            os.remove(path)
    stored['gallery'] = [g for g in gallery if g['id'] != item_id]
    write_portfolio(stored)
    return jsonify({'success': True})

# ── Contact messages ───────────────────────────────────────────────────────────
@app.route('/api/message/send', methods=['POST'])
def msg_send():
    body = request.get_json(silent=True) or {}
    name    = body.get('name',    '').strip()
    email   = body.get('email',   '').strip()
    subject = body.get('subject', '').strip()
    message = body.get('message', '').strip()

    errors = []
    if len(name) < 2:    errors.append('Name is too short')
    if '@' not in email: errors.append('Invalid email address')
    if len(message) < 5: errors.append('Message is too short')
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400

    with get_db() as conn:
        conn.execute(
            'INSERT INTO messages (name,email,subject,message) VALUES (?,?,?,?)',
            [name, email, subject, message]
        )
        conn.commit()
    return jsonify({'success': True, 'message': 'Message sent successfully!'})

@app.route('/api/message/list')
def msg_list():
    stored, ok = verify_pw(request.args.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403

    filt = request.args.get('filter', 'all')   # all | unread | read
    sort = request.args.get('sort',   'newest') # newest | oldest

    where = {'all': '', 'unread': 'WHERE is_read=0', 'read': 'WHERE is_read=1'}.get(filt, '')
    order = 'DESC' if sort != 'oldest' else 'ASC'

    with get_db() as conn:
        rows   = conn.execute(f'SELECT * FROM messages {where} ORDER BY created_at {order}').fetchall()
        total  = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
        unread = conn.execute('SELECT COUNT(*) FROM messages WHERE is_read=0').fetchone()[0]

    return jsonify({
        'success': True,
        'messages': [dict(r) for r in rows],
        'total': total,
        'unread': unread
    })

@app.route('/api/message/read', methods=['POST'])
def msg_read():
    body = request.get_json(silent=True) or {}
    _, ok = verify_pw(body.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403

    msg_id  = body.get('id', 0)
    is_read = int(body.get('is_read', 1))

    with get_db() as conn:
        if msg_id == 0:
            conn.execute('UPDATE messages SET is_read=1')
        else:
            conn.execute('UPDATE messages SET is_read=? WHERE id=?', [is_read, msg_id])
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/message/delete', methods=['POST'])
def msg_delete():
    body = request.get_json(silent=True) or {}
    _, ok = verify_pw(body.get('pw', ''))
    if not ok:
        return jsonify({'error': 'Invalid password'}), 403

    msg_id = body.get('id', 0)
    with get_db() as conn:
        if msg_id == 0:
            conn.execute('DELETE FROM messages')
        else:
            conn.execute('DELETE FROM messages WHERE id=?', [msg_id])
        conn.commit()
    return jsonify({'success': True})


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_db()
    print("─" * 58)
    print("🚀  Portfolio server starting…")
    print("   Local   →  http://localhost:5000")
    print("   Network →  http://0.0.0.0:5000")
    print("   Admin   →  click ⚙ in footer  |  pw: admin@123")
    print("─" * 58)
    app.run(host='0.0.0.0', port=5000, debug=False)
