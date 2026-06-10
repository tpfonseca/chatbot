import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage

from bike_app.i18n import t_for


def _build_message(
    to_email: str, token: str, base_url: str, lang: str = "en"
) -> tuple[str, str, str]:
    link = f"{base_url.rstrip('/')}/?verify={token}"
    subject = t_for(lang, "email_subject")
    body = t_for(lang, "email_body", link=link)
    return subject, body, link


def send_verification(
    to_email: str, token: str, base_url: str, lang: str = "en"
) -> str:
    """Send a verification email.

    Returns one of:
      "sent"        — handed off to a real provider successfully
      "dev:<link>"  — no provider configured; caller should show the link
      "error: ..."  — provider call failed
    """
    subject, body, link = _build_message(to_email, token, base_url, lang)

    api_key = os.getenv("RESEND_API_KEY")
    if api_key:
        from_addr = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
        data = json.dumps(
            {"from": from_addr, "to": [to_email], "subject": subject, "text": body}
        ).encode()
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                r.read()
            return "sent"
        except Exception as e:
            return f"error: {e}"

    smtp_host = os.getenv("SMTP_HOST")
    if smtp_host:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = os.getenv("EMAIL_FROM", "noreply@example.com")
        msg["To"] = to_email
        msg.set_content(body)
        try:
            with smtplib.SMTP(smtp_host, int(os.getenv("SMTP_PORT", "587"))) as s:
                s.starttls()
                user = os.getenv("SMTP_USER")
                if user:
                    s.login(user, os.getenv("SMTP_PASS", ""))
                s.send_message(msg)
            return "sent"
        except Exception as e:
            return f"error: {e}"

    print(f"[EMAIL DEV] To: {to_email}\nSubject: {subject}\n\n{body}\n", flush=True)
    return f"dev:{link}"
