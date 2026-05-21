import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage


def _send(subject: str, body: str, to_email: str, link: str) -> str:
    """Hand a message to the configured provider.

    Returns one of:
      "sent"        — provider accepted the message
      "dev:<link>"  — no provider configured; caller should show the link
      "error: ..."  — provider call failed
    """
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


def send_verification(to_email: str, token: str, base_url: str) -> str:
    link = f"{base_url.rstrip('/')}/?verify={token}"
    subject = "Verify your stolen bike report"
    body = (
        "Thanks for submitting a stolen bike report.\n\n"
        "Click the link below to verify your report so it appears in searches:\n\n"
        f"{link}\n\n"
        "If you didn't submit this, you can ignore this email."
    )
    return _send(subject, body, to_email, link)


def send_recovery(to_email: str, token: str, base_url: str) -> str:
    link = f"{base_url.rstrip('/')}/?recover={token}"
    subject = "Confirm your bike has been recovered"
    body = (
        "You (or someone with your email) asked to take down a stolen-bike "
        "report on Bike Check.\n\n"
        "Click the link below to confirm. Once you do, the report will stop "
        "appearing in searches:\n\n"
        f"{link}\n\n"
        "If you didn't request this, you can ignore this email — the report "
        "stays live."
    )
    return _send(subject, body, to_email, link)
