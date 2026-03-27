# 📓 Personal Notes & Reminder System

A lightweight Python system to manage notes, reminders, and screenshots — auto-published as a beautiful HTML dashboard and emailed to you via GitHub Actions every hour.

---

## 📁 Project Structure

```
├── notes_manager.py      # CLI: add notes, reminders, attachments
├── generate_html.py      # Builds docs/index.html dashboard
├── email_sender.py       # Sends reminder emails via Gmail
├── runner.py             # Hourly orchestrator (called by GitHub Actions)
├── data/
│   ├── notes.json        # Your notes & reminders (edit or use CLI)
│   └── attachments/      # Screenshot files stored here
├── docs/
│   └── index.html        # Auto-generated HTML dashboard (GitHub Pages)
└── .github/
    └── workflows/
        └── run.yml       # GitHub Actions: runs every hour
```

---

## 🚀 Setup (one-time)

### 1. Fork / Clone this repo
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### 2. Enable GitHub Pages
- Go to **Settings → Pages**
- Source: `Deploy from branch`
- Branch: `main`, folder: `/docs`
- Your dashboard will be at: `https://YOUR_USERNAME.github.io/YOUR_REPO/`

### 3. Add GitHub Secrets (for email)
Go to **Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name  | Value |
|---|---|
| `EMAIL_USER` | Your Gmail address e.g. `you@gmail.com` |
| `EMAIL_PASS` | Gmail **App Password** (not your login password) |
| `EMAIL_TO`   | Where to send reminders (can be same as above) |

> **How to get a Gmail App Password:**
> 1. Enable 2-Factor Auth on your Google account
> 2. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
> 3. Create an app password for "Mail" → copy the 16-character password

---

## 📝 How to Use

### Add a Note
```bash
python notes_manager.py add-note \
  --title "Meeting Recap" \
  --body "Discussed Q2 roadmap. Follow up with Sarah." \
  --tags "work,meeting" \
  --color blue
```

### Add a Reminder
```bash
python notes_manager.py add-reminder \
  --title "Call Doctor" \
  --body "Schedule annual checkup with Dr. Smith" \
  --due "2025-04-01 09:00" \
  --tags "health" \
  --repeat none
```
`--repeat` options: `none` | `daily` | `weekly`

### Attach a Screenshot
```bash
python notes_manager.py attach --id a1b2c3d4 --file screenshot.png
```

### List Everything
```bash
python notes_manager.py list
```

### Delete an Item
```bash
python notes_manager.py delete --id a1b2c3d4
```

---

## ⚙️ How It Works

1. **You add notes/reminders** using the CLI or by editing `data/notes.json` directly
2. **GitHub Actions runs `runner.py` every hour:**
   - Checks if any reminders are due → sends you an email
   - Regenerates `docs/index.html`
   - Commits & pushes the updated files back to your repo
3. **GitHub Pages** serves the updated dashboard automatically

---

## 📧 Email Reminder
When a reminder fires, you'll receive a rich HTML email with:
- The reminder title + description
- Tags and due date
- Any attached screenshots inline

---

## 🔁 Manual Trigger
You can manually trigger the runner anytime from:
**GitHub → Actions → Notes Runner → Run workflow**

---

## 💡 Tips
- Keep `data/notes.json` committed — that's your source of truth
- Screenshots in `data/attachments/` are embedded as base64 in the HTML
- The HTML dashboard works offline too (no CDN dependencies for core features)
- You can run `python runner.py` locally to test without GitHub Actions
