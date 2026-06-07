# 🚀 Portfolio Server — Setup Guide

Your portfolio now uses a **Flask + SQLite backend**.  
This means when YOU update your portfolio, **everyone** who visits your link sees the changes instantly.

---

## 📁 Folder Structure

```
portfolio_server/
├── app.py                  ← Flask backend (the server)
├── portfolio.db            ← SQLite database (auto-created on first run)
├── requirements.txt        ← Python packages needed
├── START_SERVER.bat        ← Double-click to start on Windows
├── start_server.sh         ← Run on Mac/Linux
├── README.md               ← This file
└── templates/
    └── index.html          ← Your portfolio (served by Flask)
```

---

## ⚡ Quick Start (Windows)

### Step 1 — Install Python
- Download from: https://www.python.org/downloads/
- ✅ During install, check **"Add Python to PATH"**

### Step 2 — Start the server
- Double-click **`START_SERVER.bat`**
- It installs packages and starts automatically

### Step 3 — Open your portfolio
- Open browser → `http://localhost:5000`

### Step 4 — Share with others (Same Wi-Fi)
- Find your IP: Open CMD → type `ipconfig` → look for **IPv4 Address**
- Share: `http://192.168.X.X:5000` (use your actual IP)
- Anyone on the **same Wi-Fi** can now see your portfolio! ✅

---

## 🌍 Share with ANYONE on the Internet (Free Hosting)

To share with people NOT on your Wi-Fi, deploy for free:

### Option A — Render.com (Recommended, Free)
1. Create account at https://render.com
2. Upload this folder to GitHub
3. New → Web Service → Connect GitHub repo
4. Set:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
5. Deploy → Get a public URL like `https://myportfolio.onrender.com`

### Option B — Railway.app (Also Free)
1. Create account at https://railway.app
2. New Project → Deploy from GitHub
3. Set start command: `python app.py`
4. Get a public URL instantly

### Option C — PythonAnywhere (Free, India-friendly)
1. Go to https://www.pythonanywhere.com
2. Sign up for free account
3. Go to **Files** → Upload all your files
4. Go to **Web** → Add a new web app → Flask
5. Set source code path to your uploaded folder
6. Done! You get `yourname.pythonanywhere.com`

---

## 🔐 Admin Panel

- Click the **⚙** icon in the footer
- Default password: **`admin@123`**
- **Change it** from Admin → Settings → Change Password after first login!
- Everything you save goes directly to the database on the server

---

## 🛠 Manual Commands (if bat file doesn't work)

Open CMD in the portfolio_server folder and run:
```bash
# Install packages
pip install flask flask-cors

# Start server
python app.py
```

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| `pip not found` | Reinstall Python and check "Add to PATH" |
| `Port 5000 already in use` | Edit `app.py`, change `port=5000` to `port=5001` |
| Others can't access my link | Make sure you're on the same Wi-Fi + check Windows Firewall |
| Changes not saving | Make sure admin panel says "✓ Saved" — check Flask console for errors |

---

## 📊 How It Works

```
Browser (Visitor)
      │
      │  GET /                → Flask serves index.html
      │  GET /api/data        → Flask returns your portfolio JSON from DB
      │
Flask Server (app.py)
      │
      │  Reads/Writes
      │
SQLite Database (portfolio.db)
      │
      └── Your portfolio content lives here!
```

Every visitor fetches the latest data from the database, so your updates are instantly visible to everyone.

---

Built with ❤️ using Python, Flask & SQLite
