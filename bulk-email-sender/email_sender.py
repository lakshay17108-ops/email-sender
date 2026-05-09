"""
Core email sending module.
Handles SMTP connection and individual email dispatch via multiple providers
(Gmail, Outlook, Zoho, Yahoo, or any custom SMTP server).
"""

import os
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


# ── Provider SMTP presets ──────────────────────────────────────────────────
EMAIL_PROVIDERS = {
    "Gmail": {"server": "smtp.gmail.com", "port": 465, "use_ssl": True},
    "Outlook / Hotmail": {"server": "smtp-mail.outlook.com", "port": 587, "use_ssl": False},
    "Zoho Mail": {"server": "smtp.zoho.com", "port": 465, "use_ssl": True},
    "Yahoo Mail": {"server": "smtp.mail.yahoo.com", "port": 465, "use_ssl": True},
    "Custom SMTP": None,  # user provides details
}


def _linkify(text: str) -> str:
    """
    Convert plain-text URLs (http/https) into clickable <a> tags.
    Already-wrapped links (<a href="...">) are left untouched.
    """
    url_pattern = re.compile(
        r'(?<!href=["\'])(?<!">)'  # not already inside an <a> tag
        r'(https?://[^\s<>"\']+)',
        re.IGNORECASE,
    )
    return url_pattern.sub(
        r'<a href="\1" target="_blank" style="color:#667eea;text-decoration:underline;">\1</a>',
        text,
    )


def send_single_email(
    smtp_server: str,
    port: int,
    sender_email: str,
    app_password: str,
    recipient_email: str,
    subject: str,
    body: str,
    use_ssl: bool = True,
    attachments: list = None,
) -> dict:
    """
    Send a single email through any SMTP provider.

    Parameters
    ----------
    smtp_server : str   – SMTP host (e.g. smtp.gmail.com)
    port : int          – SMTP port (465 for SSL, 587 for STARTTLS)
    sender_email : str  – sender address
    app_password : str  – password / app-password
    recipient_email : str
    subject : str
    body : str          – plain-text body; URLs are auto-linked in the HTML version
    use_ssl : bool      – True → SMTP_SSL on port 465;  False → STARTTLS on port 587
    attachments : list  – list of (filename, file_bytes) tuples

    Returns
    -------
    dict with 'success' (bool) and 'message' (str).
    """
    try:
        # Build the message as mixed (so attachments work alongside alt text)
        message = MIMEMultipart("mixed")
        message["Subject"] = subject
        message["From"] = sender_email
        message["To"] = recipient_email

        # ── Text alternatives (plain + HTML) ──────────────────────────
        alt_part = MIMEMultipart("alternative")

        # Plain text
        plain_part = MIMEText(body, "plain")
        alt_part.attach(plain_part)

        # HTML — auto-linkify URLs so they're clickable
        html_body = _linkify(body.replace("\n", "<br>"))
        html_part = MIMEText(
            f"""
            <html>
              <body style="font-family: 'Segoe UI', Arial, sans-serif; color: #222;">
                <p>{html_body}</p>
              </body>
            </html>
            """,
            "html",
        )
        alt_part.attach(html_part)
        message.attach(alt_part)

        # ── Attachments ───────────────────────────────────────────────
        if attachments:
            for filename, file_bytes in attachments:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(file_bytes)
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f'attachment; filename="{filename}"',
                )
                message.attach(part)

        # ── SMTP connection ───────────────────────────────────────────
        context = ssl.create_default_context()

        if use_ssl:
            # Direct SSL (port 465)
            with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient_email, message.as_string())
        else:
            # STARTTLS (port 587 – Outlook, some custom servers)
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(sender_email, app_password)
                server.sendmail(sender_email, recipient_email, message.as_string())

        return {"success": True, "message": f"✅ Sent to {recipient_email}"}

    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "message": f"❌ Authentication failed — check your email address and password / app password.",
        }
    except smtplib.SMTPRecipientsRefused:
        return {
            "success": False,
            "message": f"❌ Recipient refused: {recipient_email}",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Failed to send to {recipient_email}: {str(e)}",
        }
