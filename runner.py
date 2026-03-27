"""
runner.py — Hourly orchestrator.
Matches repo structure:
  emailsender.py   (no underscore)
  generatehtml.py  (no underscore)
  notes.json       (root level)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta

# ── Make sure THIS script's folder is on the path ────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# ── Import using YOUR actual filenames (no underscores) ──────────────────────
import importlib
emailsender  = importlib.import_module("emailsender")
generatehtml = importlib.import_module("generatehtml")

send_reminder_email = emailsender.send_reminder_email
generate_html       = generatehtml.main

# ── notes.json is in root (not data/) ────────────────────────────────────────
DATA_FILE = os.path.join(ROOT, "notes.json")


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"notes": [], "reminders": [], "trades": [], "routines": [], "routine_logs": []}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def check_and_send_reminders(data):
    now = datetime.now()
    fire_window_start = now - timedelta(minutes=65)

    for rem in data["reminders"]:
        if rem.get("sent") and rem.get("repeat", "none") == "none":
            continue
        try:
            due_dt = datetime.strptime(rem["due"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        if fire_window_start <= due_dt <= now:
            print(f"  🔔 Firing: {rem['title']}  (due {rem['due']})")
            success = send_reminder_email(rem)
            if success:
                rem["sent"] = True
                if rem.get("repeat") == "daily":
                    rem["due"] = (due_dt + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
                    rem["sent"] = False
                    print(f"     ↻ Rescheduled daily → {rem['due']}")
                elif rem.get("repeat") == "weekly":
                    rem["due"] = (due_dt + timedelta(weeks=1)).strftime("%Y-%m-%d %H:%M")
                    rem["sent"] = False
                    print(f"     ↻ Rescheduled weekly → {rem['due']}")


def git_commit_push():
    if not os.environ.get("GITHUB_ACTIONS"):
        print("  ℹ️  Not in GitHub Actions — skipping git push.")
        return
    cmds = [
        ["git", "config", "user.email", "notes-bot@github-actions"],
        ["git", "config", "user.name",  "Notes Bot"],
        ["git", "add",    "notes.json", "docs/index.html"],
        ["git", "commit", "-m",
         f"chore: auto-update [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"],
        ["git", "push"],
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 and "nothing to commit" not in (r.stdout + r.stderr):
            print(f"  ⚠️  git: {r.stderr.strip()}")
            break


def main():
    print(f"\n{'='*50}")
    print(f"  Notes Runner — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    data = load_data()

    print("\n[1/3] Checking reminders...")
    check_and_send_reminders(data)
    save_data(data)

    print("\n[2/3] Regenerating HTML...")
    generate_html()

    print("\n[3/3] Committing changes...")
    git_commit_push()

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
