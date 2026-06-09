# Portfolio — Flask + Aiven MySQL on Railway

Data lives in Aiven MySQL FOREVER. Python creates all tables automatically on startup.
No manual SQL needed on Aiven at all.

---

## Files

```
portfolio/
├── app.py              ← Flask backend (auto-creates MySQL tables)
├── requirements.txt    ← Flask, PyMySQL, cryptography (for Aiven SSL)
├── Procfile            ← Tells Railway: python app.py
├── START_SERVER.bat    ← Windows local testing
├── README.md           ← This file
└── templates/
    └── index.html      ← Portfolio frontend
```

---

## Deploy on Railway (Step by Step)

### Step 1 — Push to GitHub
Upload all files to a GitHub repository.

### Step 2 — Deploy on Railway
1. Go to https://railway.app
2. New Project → Deploy from GitHub repo → select your repo
3. Railway builds and deploys automatically

### Step 3 — Set Aiven MySQL Variables in Railway
1. Click your web service → Variables tab
2. Add these 5 variables with your Aiven values:

| Variable         | Your Aiven Value                                                    |
|-----------------|---------------------------------------------------------------------|
| MYSQL_HOST       | mysql-2c5006da-bhusareharshvardhana2122004-4ce2.h.aivencloud.com   |
| MYSQL_PORT       | 12546                                                               |
| MYSQL_USER       | avnadmin                                                            |
| MYSQL_PASSWORD   | (your Aiven password)                                               |
| MYSQL_DATABASE   | defaultdb                                                           |

3. Click Deploy

### Step 4 — Tables Created Automatically
When Flask starts it runs init_db() which:
- Creates portfolio table
- Creates messages table
- Inserts default data

You will see in Railway logs:
  Connecting to Aiven MySQL and setting up tables...
  Default portfolio data inserted
  Tables ready — portfolio and messages

NO manual SQL needed on Aiven!

### Step 5 — Open Your Portfolio
- Visit your Railway URL
- Click gear icon in footer
- Password: admin@123
- Update all your info — saved to Aiven MySQL forever

---

## Admin Panel

Profile, Skills, Projects, Achievements, Gallery, Contact, Messages, Settings

---

## How Photos Are Stored

Photos converted to base64 and stored in MySQL — no filesystem needed.
Everything survives Railway restarts and redeploys.

---

## Local Testing (XAMPP)

1. Start XAMPP MySQL
2. Create database named "portfolio" in phpMyAdmin
3. Set env vars: MYSQL_HOST=localhost, MYSQL_PORT=3306, MYSQL_USER=root, MYSQL_PASSWORD=, MYSQL_DATABASE=portfolio
4. Run: START_SERVER.bat

---

## Troubleshooting

- "Connection refused" → Check 5 MySQL variables in Railway
- "Access denied" → Check MYSQL_USER and MYSQL_PASSWORD
- SSL error → cryptography package is in requirements.txt, redeploy
- Tables not created → Check Railway logs for init_db error
- Password wrong → Default is admin@123, clear browser cache

---

Built with Python, Flask and Aiven MySQL on Railway
