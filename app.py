"""
Portfolio Backend — Flask + Aiven MySQL
- Tables are created AUTOMATICALLY on first startup
- No manual SQL needed on Aiven
- SSL is handled automatically (Aiven requires it)
- Just set 5 env vars in Railway and deploy
"""

import os, json, uuid, base64
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import pymysql
import pymysql.cursors

# ─── App ──────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates")
CORS(app)

# ─── Aiven MySQL connection config ────────────────────────────────
# Set these 5 variables in Railway → your web service → Variables tab
# Copy the values from your Aiven MySQL connection details page
DB_CONFIG = {
    "host":                os.environ.get("MYSQL_HOST",     "localhost"),
    "port":                int(os.environ.get("MYSQL_PORT", 3306)),
    "user":                os.environ.get("MYSQL_USER",     "root"),
    "password":            os.environ.get("MYSQL_PASSWORD", ""),
    "database":            os.environ.get("MYSQL_DATABASE", "defaultdb"),
    "charset":             "utf8mb4",
    "cursorclass":         pymysql.cursors.DictCursor,
    "autocommit":          True,
    "connect_timeout":     10,
    "read_timeout":        30,
    "write_timeout":       30,
    # Aiven requires SSL — these two lines handle it automatically
    "ssl_verify_cert":     False,
    "ssl_verify_identity": False,
}

def get_db():
    """Return a fresh MySQL connection to Aiven."""
    return pymysql.connect(**DB_CONFIG)

# ─── Default data seeded into MySQL on first run ──────────────────
DEFAULT = {
    "pw": "admin@123",
    "profile": {
        "firstName": "YOUR",
        "lastName":  "NAME",
        "bioShort":  "Passionate MCA Student building the future, one line of code at a time.",
        "bio":       "I'm a passionate MCA student with a strong foundation in programming and web development. I love building innovative solutions that solve real-world problems.",
        "roles":     ["MCA Student","Python Developer","Flask Developer","C++ Programmer","Prompt Engineer","Problem Solver"],
        "avatar":    ""
    },
    "skills": [
        {"id":1, "name":"Python",             "level":85, "category":"Programming"},
        {"id":2, "name":"Flask",              "level":75, "category":"Framework"},
        {"id":3, "name":"C++",               "level":70, "category":"Programming"},
        {"id":4, "name":"SQL",               "level":80, "category":"Database"},
        {"id":5, "name":"HTML",              "level":90, "category":"Web"},
        {"id":6, "name":"CSS",              "level":85, "category":"Web"},
        {"id":7, "name":"Prompt Engineering", "level":88, "category":"AI"},
        {"id":8, "name":"Presentation",       "level":82, "category":"Soft Skills"},
        {"id":9, "name":"Team Leadership",    "level":85, "category":"Soft Skills"},
        {"id":10,"name":"Communication",      "level":80, "category":"Soft Skills"},
    ],
    "projects": [
        {"id":1,"title":"Student Management System",
         "description":"A full-featured web application built with Python and Flask for managing student records, grades, and attendance with a robust MySQL database backend.",
         "tags":["Python","Flask","MySQL","HTML/CSS"],"link":"#","github":"#"},
        {"id":2,"title":"AI Prompt Toolkit",
         "description":"A comprehensive collection of optimized prompts and templates for various AI use cases, demonstrating advanced prompt engineering techniques.",
         "tags":["Prompt Engineering","AI","Python"],"link":"#","github":"#"},
    ],
    "achievements": [
        {"id":1,"title":"Academic Excellence","description":"Consistently ranked in top 10% of class throughout MCA program","year":"2024","icon":"🏆"},
        {"id":2,"title":"Hackathon Finalist","description":"Reached finals in college-level coding competition","year":"2024","icon":"⚡"},
    ],
    "gallery":  [],
    "contact":  {
        "email":"your.email@example.com","phone":"+91 XXXXXXXXXX","location":"India",
        "github":"#","linkedin":"#","twitter":"#","instagram":"#"
    },
    "cv": None,
}

# ─── DB helpers ───────────────────────────────────────────────────

def init_db():
    """
    ✅ Called at module level — runs EVERY TIME the app starts.
    Creates both tables if they don't exist yet, then seeds
    default portfolio data if the portfolio table is empty.
    NO manual SQL needed on Aiven — Python does everything.
    """
    print("⏳  Connecting to Aiven MySQL and setting up tables...")
    conn = get_db()
    try:
        with conn.cursor() as cur:

            # ── Table 1: portfolio ─────────────────────────────────
            # Stores ALL your content (profile, skills, projects etc.)
            # as one JSON record. LONGTEXT holds up to 4GB.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `portfolio` (
                    `id`   INT       NOT NULL DEFAULT 1,
                    `data` LONGTEXT  NOT NULL,
                    CONSTRAINT `pk_portfolio` PRIMARY KEY (`id`)
                ) ENGINE=InnoDB
                  DEFAULT CHARSET=utf8mb4
                  COLLATE=utf8mb4_unicode_ci
            """)

            # ── Table 2: messages ──────────────────────────────────
            # Stores every contact form submission from visitors.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `messages` (
                    `id`         INT          NOT NULL AUTO_INCREMENT,
                    `name`       VARCHAR(120) NOT NULL,
                    `email`      VARCHAR(200) NOT NULL,
                    `subject`    VARCHAR(250)          DEFAULT '',
                    `message`    TEXT         NOT NULL,
                    `is_read`    TINYINT(1)   NOT NULL DEFAULT 0,
                    `created_at` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT `pk_messages` PRIMARY KEY (`id`),
                    INDEX `idx_is_read`    (`is_read`),
                    INDEX `idx_created_at` (`created_at`)
                ) ENGINE=InnoDB
                  DEFAULT CHARSET=utf8mb4
                  COLLATE=utf8mb4_unicode_ci
            """)

            # ── Seed default data on very first run ────────────────
            cur.execute("SELECT id FROM portfolio WHERE id = 1")
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO portfolio (id, data) VALUES (1, %s)",
                    [json.dumps(DEFAULT, ensure_ascii=False)]
                )
                print("✅  Default portfolio data inserted")

        conn.commit()
        print("✅  Tables ready — portfolio and messages")

    except Exception as e:
        print(f"❌  init_db failed: {e}")
        raise
    finally:
        conn.close()


def read_db():
    """Read current portfolio data from MySQL."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT data FROM portfolio WHERE id = 1")
            row = cur.fetchone()
        if not row:
            return json.loads(json.dumps(DEFAULT))
        data = row["data"]
        return json.loads(data) if isinstance(data, str) else data
    except Exception as e:
        print(f"read_db error: {e}")
        return json.loads(json.dumps(DEFAULT))
    finally:
        conn.close()


def write_db(data: dict):
    """Save portfolio data to MySQL."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE portfolio SET data = %s WHERE id = 1",
                [json.dumps(data, ensure_ascii=False)]
            )
        conn.commit()
    except Exception as e:
        print(f"write_db error: {e}")
        raise
    finally:
        conn.close()


def check_pw(submitted: str):
    """Verify password. Returns (stored_data, is_valid)."""
    try:
        stored = read_db()
    except Exception:
        stored = json.loads(json.dumps(DEFAULT))
    return stored, submitted == stored.get("pw", "admin@123")


def file_to_b64(f) -> str:
    """Convert uploaded file to base64 data-URL (stored in MySQL)."""
    raw  = f.read()
    mime = f.content_type or "application/octet-stream"
    b64  = base64.b64encode(raw).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# ══════════════════════════════════════════════════════════════════
# AUTO SETUP — runs every time Flask starts
# Creates tables + seeds data if first run, does nothing otherwise
# ══════════════════════════════════════════════════════════════════
init_db()


# ─── Routes ───────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ping")
def ping():
    unread = 0
    db_ok  = False
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM messages WHERE is_read = 0")
            unread = cur.fetchone()["n"]
        conn.close()
        db_ok = True
    except Exception as e:
        print(f"ping error: {e}")
    return jsonify({
        "ok":     True,
        "db":     db_ok,
        "host":   DB_CONFIG["host"],
        "unread": unread,
        "time":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


# ── Portfolio data ─────────────────────────────────────────────────

@app.route("/api/data")
def api_data():
    data = read_db()
    data.pop("pw", None)
    return jsonify(data)


@app.route("/api/verify", methods=["POST"])
def api_verify():
    body = request.get_json(silent=True) or {}
    stored, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"valid": False, "error": "Wrong password"}), 403
    unread = 0
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS n FROM messages WHERE is_read = 0")
            unread = cur.fetchone()["n"]
        conn.close()
    except Exception:
        pass
    return jsonify({"valid": True, "unread": unread})


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


# ── File uploads — base64 stored in MySQL (no filesystem needed) ───

@app.route("/api/upload/avatar", methods=["POST"])
def upload_avatar():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f or not f.content_type.startswith("image/"):
        return jsonify({"error": "Please upload a valid image file"}), 400
    url = file_to_b64(f)
    stored.setdefault("profile", {})["avatar"] = url
    write_db(stored)
    return jsonify({"success": True, "url": url})


@app.route("/api/upload/gallery", methods=["POST"])
def upload_gallery():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f or not f.content_type.startswith("image/"):
        return jsonify({"error": "Please upload a valid image file"}), 400
    caption  = request.form.get("caption", "")
    url      = file_to_b64(f)
    item     = {"id": uuid.uuid4().hex, "url": url, "caption": caption}
    stored.setdefault("gallery", []).append(item)
    write_db(stored)
    return jsonify({"success": True, "item": item})


@app.route("/api/upload/cv", methods=["POST"])
def upload_cv():
    stored, ok = check_pw(request.form.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "No file received"}), 400
    allowed = {
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    }
    if f.content_type not in allowed:
        return jsonify({"error": "Only PDF, DOC, DOCX files allowed"}), 400
    url     = file_to_b64(f)
    cv_data = {"url": url, "name": secure_filename(f.filename)}
    stored["cv"] = cv_data
    write_db(stored)
    return jsonify({"success": True, "cv": cv_data})


@app.route("/api/delete/gallery", methods=["POST"])
def delete_gallery():
    body = request.get_json(silent=True) or {}
    stored, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    item_id = body.get("id")
    stored["gallery"] = [g for g in stored.get("gallery", []) if g["id"] != item_id]
    write_db(stored)
    return jsonify({"success": True})


# ── Contact messages ───────────────────────────────────────────────

@app.route("/api/message/send", methods=["POST"])
def msg_send():
    body    = request.get_json(silent=True) or {}
    name    = body.get("name",    "").strip()
    email   = body.get("email",   "").strip()
    subject = body.get("subject", "").strip()
    message = body.get("message", "").strip()

    errs = []
    if len(name)    < 2: errs.append("Name is too short")
    if "@" not in email: errs.append("Invalid email address")
    if len(message) < 5: errs.append("Message is too short")
    if errs:
        return jsonify({"error": ", ".join(errs)}), 400

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO messages (name, email, subject, message) VALUES (%s, %s, %s, %s)",
                [name, email, subject, message]
            )
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/message/list")
def msg_list():
    stored, ok = check_pw(request.args.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403

    filt  = request.args.get("filter", "all")
    order = "ASC" if request.args.get("sort") == "oldest" else "DESC"
    where = {"unread": "WHERE is_read = 0", "read": "WHERE is_read = 1"}.get(filt, "")

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM messages {where} ORDER BY created_at {order}")
            rows = cur.fetchall()
            cur.execute("SELECT COUNT(*) AS n FROM messages")
            total = cur.fetchone()["n"]
            cur.execute("SELECT COUNT(*) AS n FROM messages WHERE is_read = 0")
            unread = cur.fetchone()["n"]
        return jsonify({"success": True, "messages": rows, "total": total, "unread": unread})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/message/read", methods=["POST"])
def msg_read():
    body = request.get_json(silent=True) or {}
    _, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    mid = int(body.get("id", 0))
    r   = int(body.get("is_read", 1))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if mid == 0:
                cur.execute("UPDATE messages SET is_read = 1")
            else:
                cur.execute("UPDATE messages SET is_read = %s WHERE id = %s", [r, mid])
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@app.route("/api/message/delete", methods=["POST"])
def msg_delete():
    body = request.get_json(silent=True) or {}
    _, ok = check_pw(body.get("pw", ""))
    if not ok:
        return jsonify({"error": "Invalid password"}), 403
    mid = int(body.get("id", 0))
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if mid == 0:
                cur.execute("DELETE FROM messages")
            else:
                cur.execute("DELETE FROM messages WHERE id = %s", [mid])
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


# ─── Start ────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀  http://0.0.0.0:{port}  |  DB: {DB_CONFIG['host']}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
