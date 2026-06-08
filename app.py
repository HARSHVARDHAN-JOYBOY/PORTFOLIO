"""
Portfolio Backend — Flask + SQLite
Works on: Local (XAMPP/Windows), Render.com, PythonAnywhere, Railway
"""

import os, json, uuid, sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

# ─── App ──────────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates")
CORS(app)

BASE     = os.path.dirname(os.path.abspath(__file__))
DB       = os.path.join(BASE, "portfolio.db")
UPLOADS  = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

IMG_EXT  = {"jpg","jpeg","png","gif","webp"}
DOC_EXT  = {"pdf","doc","docx"}

# ─── Default data ─────────────────────────────────────────────────────────────
DEFAULT = {
    "pw": "admin@123",
    "profile": {
        "firstName": "YOUR", "lastName": "NAME",
        "bioShort":  "Passionate MCA Student building the future, one line of code at a time.",
        "bio":       "I'm a passionate MCA student with a strong foundation in programming and web development. I love building innovative solutions that solve real-world problems.",
        "roles":     ["MCA Student","Python Developer","Flask Developer","C++ Programmer","Prompt Engineer","Problem Solver"],
        "avatar":    ""
    },
    "skills": [
        {"id":1,"name":"Python","level":85,"category":"Programming"},
        {"id":2,"name":"Flask","level":75,"category":"Framework"},
        {"id":3,"name":"C++","level":70,"category":"Programming"},
        {"id":4,"name":"SQL","level":80,"category":"Database"},
        {"id":5,"name":"HTML","level":90,"category":"Web"},
        {"id":6,"name":"CSS","level":85,"category":"Web"},
        {"id":7,"name":"Prompt Engineering","level":88,"category":"AI"},
        {"id":8,"name":"Presentation","level":82,"category":"Soft Skills"},
        {"id":9,"name":"Team Leadership","level":85,"category":"Soft Skills"},
        {"id":10,"name":"Communication","level":80,"category":"Soft Skills"}
    ],
    "projects": [
        {"id":1,"title":"Student Management System","description":"A full-featured web application built with Python and Flask for managing student records, grades, and attendance with a robust SQL database backend.","tags":["Python","Flask","SQL","HTML/CSS"],"link":"#","github":"#"},
        {"id":2,"title":"AI Prompt Toolkit","description":"A comprehensive collection of optimized prompts and templates for various AI use cases, demonstrating advanced prompt engineering techniques.","tags":["Prompt Engineering","AI","Python"],"link":"#","github":"#"}
    ],
    "achievements": [
        {"id":1,"title":"Academic Excellence","description":"Consistently ranked in top 10% of class throughout MCA program","year":"2024","icon":"🏆"},
        {"id":2,"title":"Hackathon Finalist","description":"Reached finals in college-level coding competition with Flask solution","year":"2024","icon":"⚡"}
    ],
    "gallery":  [],
    "contact":  {"email":"your.email@example.com","phone":"+91 XXXXXXXXXX","location":"India","github":"#","linkedin":"#","twitter":"#","instagram":"#"},
    "cv":       None
}

# ─── DB helpers ───────────────────────────────────────────────────────────────
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables and seed default data. Called at module load."""
    with db() as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS portfolio (
                id   INTEGER PRIMARY KEY,
                data TEXT    NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                email      TEXT    NOT NULL,
                subject    TEXT    DEFAULT '',
                message    TEXT    NOT NULL,
                is_read    INTEGER DEFAULT 0,
                created_at TEXT    DEFAULT (datetime('now','localtime'))
            )""")
        if not c.execute("SELECT id FROM portfolio WHERE id=1").fetchone():
            c.execute("INSERT INTO portfolio VALUES (1,?)", [json.dumps(DEFAULT)])
        c.commit()

# ── Call init_db HERE at module level so it always runs,
#    whether started via 'python app.py' OR gunicorn/render ──────────────────
init_db()

def read_db():
    with db() as c:
        row = c.execute("SELECT data FROM portfolio WHERE id=1").fetchone()
        return json.loads(row["data"]) if row else json.loads(json.dumps(DEFAULT))

def write_db(data):
    with db() as c:
        c.execute("UPDATE portfolio SET data=? WHERE id=1", [json.dumps(data)])
        c.commit()

def check_pw(submitted):
    """Return (stored, is_valid). Safe even if DB is empty."""
    try:
        stored = read_db()
    except Exception:
        stored = json.loads(json.dumps(DEFAULT))
    return stored, submitted == stored.get("pw", "admin@123")

def ext(filename):
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

def save_file(f, prefix):
    name = f"{prefix}_{uuid.uuid4().hex[:10]}.{ext(f.filename)}"
    f.save(os.path.join(UPLOADS, name))
    return f"/uploads/{name}"

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/uploads/<path:filename>")
def serve_upload(filename):
    return send_from_directory(UPLOADS, filename)

# ── Ping ──────────────────────────────────────────────────────────────────────
@app.route("/api/ping")
def ping():
    unread = 0
    try:
        with db() as c:
            unread = c.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()[0]
    except Exception:
        pass
    return jsonify({"ok": True, "db": os.path.exists(DB), "unread": unread,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

# ── Portfolio data ─────────────────────────────────────────────────────────────
@app.route("/api/data")
def api_data():
    data = read_db()
    data.pop("pw", None)
    return jsonify(data)

@app.route("/api/verify", methods=["POST"])
def api_verify():
    body = request.get_json(silent=True) or {}
    stored, ok = check_pw(body.get("pw", ""))
    if ok:
        unread = 0
        try:
            with db() as c:
                unread = c.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()[0]
        except Exception:
            pass
        return jsonify({"valid": True, "unread": unread})
    return jsonify({"valid": False, "error": "Wrong password"}), 403

@app.route("/api/save", methods=["POST"])
def api_save():
    body = request.get_json(silent=True) or {}
    stored, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    new = body.get("data", {})
    stored.update(new)
    if new.get("pw"):
        stored["pw"] = new["pw"]
    try:
        write_db(stored)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/reset", methods=["POST"])
def api_reset():
    body = request.get_json(silent=True) or {}
    _, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    write_db(json.loads(json.dumps(DEFAULT)))
    return jsonify({"success": True})

# ── Uploads ───────────────────────────────────────────────────────────────────
@app.route("/api/upload/avatar", methods=["POST"])
def upload_avatar():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f or ext(f.filename) not in IMG_EXT:
        return jsonify({"error": "No valid image file"}), 400
    # Remove old avatar file
    old = stored.get("profile", {}).get("avatar", "")
    if old.startswith("/uploads/"):
        old_path = os.path.join(UPLOADS, os.path.basename(old))
        if os.path.exists(old_path):
            try: os.remove(old_path)
            except Exception: pass
    url = save_file(f, "avatar")
    stored["profile"]["avatar"] = url
    write_db(stored)
    return jsonify({"success": True, "url": url})

@app.route("/api/upload/gallery", methods=["POST"])
def upload_gallery():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f or ext(f.filename) not in IMG_EXT:
        return jsonify({"error": "No valid image file"}), 400
    caption = request.form.get("caption", "")
    url = save_file(f, "gallery")
    item = {"id": uuid.uuid4().hex, "url": url, "caption": caption}
    stored.setdefault("gallery", []).append(item)
    write_db(stored)
    return jsonify({"success": True, "item": item})

@app.route("/api/upload/cv", methods=["POST"])
def upload_cv():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f or ext(f.filename) not in DOC_EXT:
        return jsonify({"error": "Only PDF, DOC, DOCX allowed"}), 400
    # Remove old CV
    old_cv = stored.get("cv") or {}
    old_url = old_cv.get("url", "")
    if old_url.startswith("/uploads/"):
        old_path = os.path.join(UPLOADS, os.path.basename(old_url))
        if os.path.exists(old_path):
            try: os.remove(old_path)
            except Exception: pass
    url = save_file(f, "cv")
    stored["cv"] = {"url": url, "name": secure_filename(f.filename)}
    write_db(stored)
    return jsonify({"success": True, "cv": stored["cv"]})

@app.route("/api/delete/gallery", methods=["POST"])
def delete_gallery():
    body = request.get_json(silent=True) or {}
    stored, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    item_id = body.get("id")
    gallery = stored.get("gallery", [])
    item = next((g for g in gallery if g["id"] == item_id), None)
    if item and item["url"].startswith("/uploads/"):
        path = os.path.join(UPLOADS, os.path.basename(item["url"]))
        if os.path.exists(path):
            try: os.remove(path)
            except Exception: pass
    stored["gallery"] = [g for g in gallery if g["id"] != item_id]
    write_db(stored)
    return jsonify({"success": True})

# ── Messages ──────────────────────────────────────────────────────────────────
@app.route("/api/message/send", methods=["POST"])
def msg_send():
    body = request.get_json(silent=True) or {}
    name    = body.get("name",    "").strip()
    email   = body.get("email",   "").strip()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()
    errs = []
    if len(name) < 2:     errs.append("Name too short")
    if "@" not in email:  errs.append("Invalid email")
    if len(message) < 5:  errs.append("Message too short")
    if errs:
        return jsonify({"error": ", ".join(errs)}), 400
    try:
        with db() as c:
            c.execute("INSERT INTO messages (name,email,subject,message) VALUES (?,?,?,?)",
                      [name, email, subject, message])
            c.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/message/list")
def msg_list():
    stored, ok = check_pw(request.args.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    filt  = request.args.get("filter", "all")
    order = "ASC" if request.args.get("sort") == "oldest" else "DESC"
    where = {"unread":"WHERE is_read=0","read":"WHERE is_read=1"}.get(filt,"")
    try:
        with db() as c:
            rows   = c.execute(f"SELECT * FROM messages {where} ORDER BY created_at {order}").fetchall()
            total  = c.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            unread = c.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()[0]
        return jsonify({"success":True,"messages":[dict(r) for r in rows],"total":total,"unread":unread})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/message/read", methods=["POST"])
def msg_read():
    body = request.get_json(silent=True) or {}
    _, ok = check_pw(body.get("pw",""))
    if not ok: return jsonify({"error":"Invalid password"}), 403
    mid = int(body.get("id", 0))
    r   = int(body.get("is_read", 1))
    try:
        with db() as c:
            if mid == 0: c.execute("UPDATE messages SET is_read=1")
            else:        c.execute("UPDATE messages SET is_read=? WHERE id=?", [r, mid])
            c.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/message/delete", methods=["POST"])
def msg_delete():
    body = request.get_json(silent=True) or {}
    _, ok = check_pw(body.get("pw",""))
    if not ok: return jsonify({"error":"Invalid password"}), 403
    mid = int(body.get("id", 0))
    try:
        with db() as c:
            if mid == 0: c.execute("DELETE FROM messages")
            else:        c.execute("DELETE FROM messages WHERE id=?", [mid])
            c.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀  Running at http://0.0.0.0:{port}")
    print("   Admin password: admin@123")
    print("   Press Ctrl+C to stop\n")
    app.run(host="0.0.0.0", port=port, debug=False)
