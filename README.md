# Portfolio — Flask + SQLite

Complete portfolio with admin panel, contact inbox, photo upload, and server-side storage.
Deployable on Render.com (free), PythonAnywhere (free), or local XAMPP/PC.

---

## Files

```
portfolio/
├── app.py               ← Flask backend (all API routes)
├── requirements.txt     ← Python packages
├── Procfile             ← Tells Render how to start the app
├── START_SERVER.bat     ← Double-click to run on Windows
├── start_server.sh      ← Run on Mac/Linux
├── README.md            ← This file
├── portfolio.db         ← SQLite database (auto-created on first run)
├── uploads/             ← Uploaded photos & CV (auto-created)
└── templates/
    └── index.html       ← Portfolio frontend
```

---

## Run Locally (Windows)

1. Install Python → https://www.python.org ✅ tick **Add to PATH**
2. Double-click **START_SERVER.bat**
3. Open `http://localhost:5000`

---

## Deploy on Render.com (Free — Recommended)

### Step 1 — Push to GitHub
1. Create a free account at https://github.com
2. Create a new repository (e.g. `my-portfolio`)
3. Upload all project files to the repository

### Step 2 — Connect to Render
1. Go to https://render.com → sign up free
2. Click **New** → **Web Service**
3. Connect your GitHub account → select your repository

### Step 3 — Configure Render Settings
Fill in these fields exactly:

| Field | Value |
|-------|-------|
| **Name** | my-portfolio (any name) |
| **Environment** | Python |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python app.py` |
| **Plan** | Free |

4. Click **Create Web Service**
5. Wait 2-3 minutes for deployment
6. Click the URL Render gives you — your portfolio is live!

### Step 4 — Admin Panel on Render
- Open your Render URL
- Click the **⚙** gear icon in footer
- Password: `admin@123`
- Update all your info — it saves to the server and everyone sees it!

---

## Important: Data Persistence on Render Free Tier

Render's free tier has an **ephemeral filesystem** — this means:
- Data saved to `portfolio.db` and `uploads/` **persists while the server is running**
- If Render restarts your service (happens after inactivity or redeploy), the database resets

### Solution — Use the Export/Import feature:
1. Go to Admin Panel → Settings → **Export JSON Backup**
2. Save the downloaded `portfolio-backup.json` file safely
3. After any redeploy, go to Admin → Settings → **Import JSON**
4. Re-upload your photos via the Gallery and Profile tabs

### Better Solution — Render Persistent Disk ($7/month):
- In Render dashboard → your service → **Disks** → Add Disk
- Mount path: `/opt/render/project/src`
- This keeps your data permanently across restarts

---

## Deploy on PythonAnywhere (Free — Data Persists!)

PythonAnywhere's free tier has a **persistent filesystem** — data never resets!

1. Sign up free at https://www.pythonanywhere.com
2. Go to **Files** tab → upload all project files to `/home/yourusername/portfolio/`
3. Go to **Consoles** → Bash console:
   ```bash
   cd portfolio
   pip install flask flask-cors werkzeug
   python app.py   # test it runs (Ctrl+C to stop)
   ```
4. Go to **Web** tab → **Add a new web app**
5. Choose **Manual configuration** → Python 3.10
6. Set:
   - Source code: `/home/yourusername/portfolio`
   - Working directory: `/home/yourusername/portfolio`
   - WSGI file — click it and replace content with:
     ```python
     import sys
     sys.path.insert(0, '/home/yourusername/portfolio')
     from app import app as application
     ```
7. Click **Reload** → visit `yourusername.pythonanywhere.com`

---

## Admin Panel Features

| Tab | What You Can Do |
|-----|----------------|
| 👤 Profile | Name, bio, roles (typewriter), photo upload, CV upload |
| 💡 Skills | Add/delete skills, drag slider to set 0–100% level |
| 🚀 Projects | Add/delete with tags, live demo & GitHub links |
| 🏆 Achievements | Add/delete with emoji icons and year |
| 📸 Gallery | Upload photos directly from phone/PC |
| 📬 Contact | Email, phone, location, social links |
| 📩 Messages | Read/reply/delete all contact form messages |
| ⚙️ Settings | Change password, export/import backup, reset |

---

## Why the Old Version Had Wrong Password Error

The old version had this bug:

```python
# OLD — BROKEN on Render/Gunicorn
if __name__ == '__main__':
    init_db()   ← Never runs on Render!
    app.run(...)
```

When Render starts your app, it doesn't use `python app.py` directly — so `init_db()` never ran, meaning the database had no tables, and every password check threw an error (which Flask silently returned as "wrong password").

**This version fixes it:**

```python
# NEW — FIXED, runs ALWAYS
def init_db(): ...

init_db()   ← Called at module level, always runs

if __name__ == '__main__':
    app.run(...)
```

Also fixed: Render sets a `PORT` environment variable. The app now reads it:
```python
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Password not working | Default is `admin@123` — try clearing browser cache |
| Site shows "Your Name" after redeploy | Export JSON before redeploy, import after |
| Photo upload fails on Render free | Use PythonAnywhere instead (persistent disk) |
| Port already in use locally | Edit `app.py` → change `port=5000` to `port=5001` |
| `Module not found` error | Run `pip install flask flask-cors werkzeug` |
| Data missing after Render restart | See "Data Persistence" section above |

---

Built with Python, Flask & SQLite
