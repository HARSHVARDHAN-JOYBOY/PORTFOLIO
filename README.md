# 🚀 Portfolio — Flask + SQLite (Python)

A complete portfolio website with admin panel, real file uploads,
contact message inbox, and server-side data storage.

---

## 📁 Project Structure

```
flask_portfolio/
├── app.py                 ← Flask backend (all API routes)
├── requirements.txt       ← Python packages
├── START_SERVER.bat       ← Double-click to run on Windows
├── start_server.sh        ← Run on Mac/Linux
├── portfolio.db           ← SQLite database (auto-created)
├── uploads/               ← Uploaded photos & CV files (auto-created)
├── templates/
│   └── index.html         ← Complete portfolio frontend
└── README.md              ← This file
```

---

## ⚡ Quick Start

### Windows
1. Install Python from https://www.python.org ✅ tick **"Add to PATH"**
2. Double-click **`START_SERVER.bat`**
3. Open browser → `http://localhost:5000`

### Mac / Linux
```bash
pip3 install flask flask-cors werkzeug
python3 app.py
```
Then open `http://localhost:5000`

---

## 🌐 Share With Others

### Same Wi-Fi Network
1. Find your IP: Open CMD → type `ipconfig` → copy **IPv4 Address**
2. Share: `http://192.168.X.X:5000`

### Everyone on the Internet (Free Hosting)

**PythonAnywhere (Easiest — Free)**
1. Sign up at https://www.pythonanywhere.com
2. Go to **Files** → upload all project files
3. Go to **Web** → Add new web app → Flask
4. Set source directory to your upload folder
5. Done! You get `yourname.pythonanywhere.com`

**Render.com (Also Free)**
1. Push project to GitHub
2. Go to https://render.com → New → Web Service
3. Connect GitHub repo
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `python app.py`
6. Deploy → get public URL

---

## 🔐 Admin Panel

| Detail | Value |
|--------|-------|
| Access | Click **⚙** icon in page footer |
| Default password | `admin@123` |
| Change password | Admin → Settings tab |

---

## 📋 What You Can Manage

| Tab | Features |
|-----|---------|
| 👤 Profile | Name, bio, roles (typewriter), photo upload, CV upload |
| 💡 Skills | Add/delete skills, drag sliders to set level 0–100% |
| 🚀 Projects | Add/delete projects with tags, live demo & GitHub links |
| 🏆 Achievements | Add/delete with emoji icons and year |
| 📸 Gallery | Upload photos directly (real files saved on server) |
| 📬 Contact | Email, phone, location, all social links |
| 📩 Messages | Read/reply/delete all contact form messages |
| ⚙️ Settings | Change password, export/import/reset data |

---

## 📩 Contact Messages

When someone fills your contact form:
- Message is saved to **SQLite database** on your server
- You see a **red unread badge** on the 📩 Messages tab
- Open admin → Messages tab to:
  - Read all messages
  - Reply directly via email (opens your email client)
  - Mark as Read / Unread
  - Delete individual messages or all at once

---

## 🗃️ Database Structure

```
portfolio.db
├── portfolio table  →  id=1, data (JSON string with all your info)
└── messages table   →  id, name, email, subject, message, is_read, created_at
```

---

## 🖼️ File Uploads

All uploads are stored as real files (not base64 blobs):

```
uploads/
├── avatar_abc123.jpg    ← your profile photo
├── cv_def456.pdf        ← your resume
├── gallery_ghi789.png   ← gallery photo 1
└── gallery_jkl012.jpg   ← gallery photo 2
```

**Limits:** Images max 5MB | CV max 10MB | Formats: JPG, PNG, GIF, WEBP (images), PDF/DOC/DOCX (CV)

---

## 🔗 API Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/api/ping` | Server health check + unread count |
| GET | `/api/data` | Get full portfolio data (no password) |
| POST | `/api/verify-pw` | Verify admin password |
| POST | `/api/save` | Save portfolio data |
| POST | `/api/reset` | Reset to defaults |
| POST | `/api/upload/avatar` | Upload profile photo |
| POST | `/api/upload/gallery` | Upload gallery photo |
| POST | `/api/upload/cv` | Upload CV/Resume |
| POST | `/api/delete/gallery-item` | Delete a gallery photo |
| POST | `/api/message/send` | Send contact message (public) |
| GET | `/api/message/list` | List messages (admin) |
| POST | `/api/message/read` | Mark message read/unread (admin) |
| POST | `/api/message/delete` | Delete message(s) (admin) |

---

## 🐛 Bugs Fixed vs Old Version

| Old Bug | Fixed |
|---------|-------|
| Contact form used `mailto:` — no messages stored | ✅ Saves to SQLite |
| Photos stored as base64 in JSON blob — huge DB | ✅ Real files in `/uploads/` |
| CV stored as base64 blob — very large | ✅ Real file in `/uploads/` |
| `resetData()` didn't call Flask route | ✅ Calls `/api/reset` properly |
| No `/api/ping` health check | ✅ Added |
| No messages inbox | ✅ Full CRUD inbox in admin |
| No server status indicator | ✅ Green/red dot in nav |

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `python not found` | Reinstall Python, tick "Add Python to PATH" |
| Port 5000 in use | Edit `app.py` → change `port=5000` to `port=5001` |
| Photos not saving | Make sure `uploads/` folder exists (auto-created on first run) |
| Admin password forgotten | Delete `portfolio.db` → restart server → default `admin@123` restored |
| Changes not visible to others | Make sure server is running on `0.0.0.0` (already set in `app.py`) |
| `Module not found` error | Run `pip install flask flask-cors werkzeug` |

---

Built with ❤️ using Python, Flask & SQLite
