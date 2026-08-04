"""
emailer.py — Maid In Salt Lake City
Sends invoice PDFs from maidinslc@gmail.com via Gmail SMTP.

Requires these entries in Streamlit secrets:

    [gmail]
    address = "maidinslc@gmail.com"
    app_password = "abcdefghijklmnop"   # 16-char Google App Password, no spaces

Nothing else to install — smtplib ships with Python.
"""

import smtplib
from email.message import EmailMessage

# Who can appear on the signature. Add or edit freely.
SENDERS = {
    "Carmen Flores Gilmore": {"title": "Owner", "phone": "(801) 882-6510"},
    "Maddie Thomas":         {"title": "Office Manager", "phone": "(801) 928-4702"},
    "Victor Flores":         {"title": "Operations", "phone": "(801) 708-4014"},
}

ADDRESS = "54 W Inglenook Dr Apt 811, Midvale, UT 84047-5328"


def signature(sender_name):
    s = SENDERS.get(sender_name, {})
    return (f"\n\n{sender_name}\n"
            f"{s.get('title','')}, Maid In Salt Lake City, LLC\n"
            f"{s.get('phone','')} | maidinslc@gmail.com\n"
            f"https://www.maidinslc.com/\n"
            f"{ADDRESS}")


def build_body(lines, sender_name, greeting_name=""):
    """lines: list of strings describing each invoice."""
    hello = f"Hi {greeting_name}," if greeting_name.strip() else "Hi,"
    items = "\n".join(f"\u2022 {ln}" for ln in lines)
    return f"{hello}\n\nSee attached:\n\n{items}\n\nThanks!{signature(sender_name)}"


def send_invoice_email(to_addrs, subject, body, attachments,
                       gmail_address, app_password, cc_addrs=None):
    """
    to_addrs / cc_addrs : list of email strings
    attachments         : list of (filename, pdf_bytes) tuples
    Returns (True, "") on success or (False, "error text") on failure.
    """
    to_addrs = [a.strip() for a in to_addrs if a and a.strip()]
    cc_addrs = [a.strip() for a in (cc_addrs or []) if a and a.strip()]
    if not to_addrs:
        return False, "No recipient email address."

    msg = EmailMessage()
    msg["From"] = f"Maid In Salt Lake City, LLC <{gmail_address}>"
    msg["To"] = ", ".join(to_addrs)
    if cc_addrs:
        msg["Cc"] = ", ".join(cc_addrs)
    msg["Subject"] = subject
    msg.set_content(body)

    for fname, data in attachments:
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=fname)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(gmail_address, app_password.replace(" ", ""))
            smtp.send_message(msg, to_addrs=to_addrs + cc_addrs)
        return True, ""
    except smtplib.SMTPAuthenticationError:
        return False, ("Gmail rejected the login. Check that the app password in "
                       "Streamlit secrets is current and has no spaces.")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"
