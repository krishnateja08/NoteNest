"""
email_sender.py — Sends reminder emails via Gmail SMTP.
Set these GitHub Secrets (or .env):
  EMAIL_USER   — your Gmail address
  EMAIL_PASS   — Gmail App Password (not your login password)
  EMAIL_TO     — recipient address
"""

import os
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime


def build_html_email(reminder: dict) -> str:
    """Generate a rich HTML email body for a reminder."""
    title = reminder.get("title", "Reminder")
    body = reminder.get("body", "")
    due = reminder.get("due", "")
    tags = reminder.get("tags", [])
    tag_html = "".join(
        f'<span style="background:#f0a500;color:#1a1a2e;padding:2px 10px;'
        f'border-radius:20px;font-size:12px;margin-right:6px;">#{t}</span>'
        for t in tags
    )
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Georgia', serif; background: #f7f3ee; margin: 0; padding: 20px; }}
    .card {{ background: #1a1a2e; color: #e8d5b7; border-radius: 16px; max-width: 560px;
             margin: 0 auto; padding: 36px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
    .badge {{ display:inline-block; background:#f0a500; color:#1a1a2e; border-radius:8px;
              padding:4px 14px; font-size:13px; font-weight:bold; margin-bottom:18px; }}
    h1 {{ font-size: 26px; margin: 0 0 12px; color: #f0a500; }}
    .body-text {{ font-size: 16px; line-height: 1.7; color: #d4c5a9; margin: 16px 0; }}
    .due {{ font-size: 14px; color: #9e8c6e; margin-top: 20px; border-top: 1px solid #2e2e50;
            padding-top: 14px; }}
    .footer {{ text-align: center; font-size: 12px; color: #9e8c6e; margin-top: 24px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="badge">⏰ REMINDER</div>
    <h1>{title}</h1>
    <div class="body-text">{body if body else "<em>No description provided.</em>"}</div>
    <div style="margin-top:14px;">{tag_html}</div>
    <div class="due">📅 Due: <strong>{due}</strong><br>
         🕐 Sent at: {datetime.now().strftime("%Y-%m-%d %H:%M")}</div>
    <div class="footer">Sent by your Personal Notes & Reminder System 📓</div>
  </div>
</body>
</html>
"""


def send_reminder_email(reminder: dict):
    """Send a reminder email. Returns True on success."""
    email_user = os.environ.get("EMAIL_USER", "")
    email_pass = os.environ.get("EMAIL_PASS", "")
    email_to   = os.environ.get("EMAIL_TO", email_user)

    if not email_user or not email_pass:
        print("⚠️  EMAIL_USER / EMAIL_PASS not set — skipping email.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"⏰ Reminder: {reminder.get('title', 'You have a reminder!')}"
    msg["From"]    = email_user
    msg["To"]      = email_to

    plain_text = (
        f"REMINDER: {reminder.get('title')}\n\n"
        f"{reminder.get('body', '')}\n\n"
        f"Due: {reminder.get('due')}"
    )
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(build_html_email(reminder), "html"))

    # Attach screenshot files if any
    for filepath in reminder.get("attachments", []):
        if os.path.exists(filepath):
            with open(filepath, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(filepath)}",
            )
            msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(email_user, email_pass)
            server.sendmail(email_user, email_to, msg.as_string())
        print(f"📧 Email sent → {email_to}  [{reminder.get('title')}]")
        return True
    except Exception as e:
        print(f"❌ Email failed: {e}")
        return False
