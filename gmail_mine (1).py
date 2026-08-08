"""
gmail_mine.py — Maid In Salt Lake City
Reads the Gmail Sent folder over IMAP to recover billing addresses from
invoices already sent. Uses the same app password as sending — no new setup.
"""

import imaplib
import email
import re
from email.header import decode_header, make_header
from datetime import datetime, timedelta

SENT_CANDIDATES = ['"[Gmail]/Sent Mail"', '"[Google Mail]/Sent Mail"', "Sent"]
ADDR = re.compile(r"[\w\.\+\-]+@[\w\-]+\.[\w\.\-]+")


def _decode(v):
    try:
        return str(make_header(decode_header(v or "")))
    except Exception:
        return v or ""


def scan_sent(address, app_password, months_back=24, keyword="invoice", limit=400):
    """
    Return recipients found on sent mail matching `keyword`:
      [{email, name, count, last_date, subjects:[...]}]
    """
    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(address, app_password.replace(" ", ""))

    folder = None
    for cand in SENT_CANDIDATES:
        try:
            typ, _ = m.select(cand, readonly=True)
            if typ == "OK":
                folder = cand
                break
        except Exception:
            continue
    if not folder:
        m.logout()
        raise RuntimeError("Could not open the Gmail Sent folder.")

    since = (datetime.utcnow() - timedelta(days=30 * months_back)).strftime("%d-%b-%Y")
    typ, data = m.search(None, f'(SINCE {since} SUBJECT "{keyword}")')
    ids = data[0].split()[-limit:] if data and data[0] else []

    people = {}
    for i in ids:
        typ, raw = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (TO CC SUBJECT DATE)])")
        if typ != "OK" or not raw or not raw[0]:
            continue
        msg = email.message_from_bytes(raw[0][1])
        subj = _decode(msg.get("Subject", ""))
        when = ""
        try:
            when = email.utils.parsedate_to_datetime(msg.get("Date", "")).date().isoformat()
        except Exception:
            pass

        recips = f"{msg.get('To','')} {msg.get('Cc','')}"
        for name, addr in email.utils.getaddresses([recips]):
            addr = addr.strip().lower()
            if not ADDR.fullmatch(addr) or addr == address.lower():
                continue
            p = people.setdefault(addr, {"email": addr, "name": _decode(name),
                                         "count": 0, "last_date": "", "subjects": []})
            p["count"] += 1
            if _decode(name) and not p["name"]:
                p["name"] = _decode(name)
            if when > p["last_date"]:
                p["last_date"] = when
            if subj and len(p["subjects"]) < 5:
                p["subjects"].append(subj)

    m.close()
    m.logout()
    return sorted(people.values(), key=lambda p: (-p["count"], p["email"]))


def suggest_for_client(client_name, people):
    """Rank recipients by how well they match a client name."""
    words = [w for w in re.sub(r"[^a-z ]", " ", str(client_name).lower()).split() if len(w) > 3]
    scored = []
    for p in people:
        blob = (p["email"] + " " + p["name"] + " " + " ".join(p["subjects"])).lower()
        hits = sum(1 for w in words if w in blob)
        if hits:
            scored.append((hits, p))
    return [p for _, p in sorted(scored, key=lambda t: -t[0])]


# ----------------------------------------------------------------------
# Recover past invoices from PDF attachments in Sent mail
# ----------------------------------------------------------------------
MONEY = re.compile(r"TOTAL\s*DUE\s*\$?\s*([\d,]+\.\d{2})", re.I)
INVNO = re.compile(r"Invoice\s*No\.?\s*([A-Za-z0-9\-]+)", re.I)


def scan_invoice_attachments(address, app_password, months_back=24, limit=150):
    """
    Find PDF attachments on sent mail and read the invoice number and total
    out of each. Returns:
      [{date, to, filename, invoice_no, amount, subject}]
    """
    try:
        from pypdf import PdfReader
    except Exception:
        PdfReader = None
    import io

    m = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    m.login(address, app_password.replace(" ", ""))

    folder = None
    for cand in SENT_CANDIDATES:
        try:
            typ, _ = m.select(cand, readonly=True)
            if typ == "OK":
                folder = cand
                break
        except Exception:
            continue
    if not folder:
        m.logout()
        raise RuntimeError("Could not open the Gmail Sent folder.")

    since = (datetime.utcnow() - timedelta(days=30 * months_back)).strftime("%d-%b-%Y")
    typ, data = m.search(None, f'(SINCE {since} HAS attachment)')
    ids = data[0].split()[-limit:] if data and data[0] else []

    found = []
    for i in ids:
        typ, raw = m.fetch(i, "(RFC822)")
        if typ != "OK" or not raw or not raw[0]:
            continue
        msg = email.message_from_bytes(raw[0][1])
        subj = _decode(msg.get("Subject", ""))
        when = ""
        try:
            when = email.utils.parsedate_to_datetime(msg.get("Date", "")).date().isoformat()
        except Exception:
            pass
        tos = [a for _, a in email.utils.getaddresses([msg.get("To", "") + " " + msg.get("Cc", "")])
               if a and a.lower() != address.lower()]

        for part in msg.walk():
            fn = _decode(part.get_filename() or "")
            if not fn.lower().endswith(".pdf"):
                continue
            rec = {"date": when, "to": ", ".join(tos), "filename": fn,
                   "invoice_no": "", "amount": 0.0, "subject": subj}
            if PdfReader:
                try:
                    payload = part.get_payload(decode=True) or b""
                    text = "\n".join((pg.extract_text() or "")
                                     for pg in PdfReader(io.BytesIO(payload)).pages)
                    mo = MONEY.search(text)
                    if mo:
                        rec["amount"] = float(mo.group(1).replace(",", ""))
                    no = INVNO.search(text)
                    if no:
                        rec["invoice_no"] = no.group(1)
                except Exception:
                    pass
            found.append(rec)

    m.close()
    m.logout()
    found.sort(key=lambda r: r["date"])
    return found
