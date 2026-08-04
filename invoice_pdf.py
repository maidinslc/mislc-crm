"""
invoice_pdf.py — Maid In Salt Lake City
Drop this file into your CRM repo next to app.py.

Usage:
    from invoice_pdf import build_invoice
    pdf_bytes = build_invoice({
        "invoice_no": "1004",
        "date": "08/04/2026",
        "client": "Parc View Apartments",
        "addr1": "Attn: Accounts Payable",
        "addr2": "Midvale, UT",
        "description": "Unit turnover cleaning - Unit #2201",
        "detail": "Serviced Monday, August 3, 2026",
        "qty": 1,
        "rate": 150.00,
        "tax": 0,
        "po": "Unit #2201",
    })

Returns raw PDF bytes — feed straight into st.download_button.
Requires: reportlab
"""

import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

# ---------- Brand ----------
PINK_BAR = HexColor("#F8DFDB")
ACCENT = HexColor("#E0A79C")
DARK = HexColor("#1A1A1A")
GREY = HexColor("#666666")
LINE = HexColor("#CFCFCF")

LOGO_B64 = "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"

BIZ = [
    ("Maid In Salt Lake City", True),
    ("54 W Inglenook Dr Apt 811", False),
    ("Midvale, UT 84047", False),
    ("801-708-4014", False),
    ("maidinslc@gmail.com", False),
]

def _pay_text(job):
    t = str(job.get('terms') or "Due upon receipt").strip()
    due = str(job.get('due','')).strip()
    if t.lower().startswith("net"):
        lead = f"Payment terms are {t}" + (f", due {due}." if due else ".")
    else:
        lead = "Payment is due upon receipt."
    return (lead + " Please make checks payable to Maid In Salt Lake City. "
            "To pay by card, Venmo, or Zelle, call or text 801-708-4014.")

W, H = letter
L, R = 55, 557
COL2 = 314
X_QTY, X_RATE, X_AMT = 375, 470, R - 4


def _y(top):
    return H - top


def _money(v):
    return "${:,.2f}".format(float(v))


def build_invoice(job):
    """job: dict. Returns PDF file bytes."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(f"Invoice {job.get('invoice_no','')} - Maid In Salt Lake City")

    # Logo
    try:
        c.drawImage(ImageReader(io.BytesIO(base64.b64decode(LOGO_B64))),
                    L, _y(133), width=68, height=69,
                    preserveAspectRatio=True, mask='auto')
    except Exception:
        pass

    # Title block
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 34)
    c.drawRightString(R, _y(100), "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawRightString(R, _y(118), f"Invoice No.  {job.get('invoice_no','')}")
    c.drawRightString(R, _y(133), f"Date  \u00b7  {job.get('date','')}")

    c.setStrokeColor(ACCENT)
    c.setLineWidth(1)
    c.line(L, _y(160), R, _y(160))

    # FROM
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(L, _y(176), "FROM")
    ty = 190
    for text, bold in BIZ:
        c.setFillColor(DARK if bold else GREY)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        c.drawString(L, _y(ty), text)
        ty += 14

    # BILL TO
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(COL2, _y(176), "BILL TO")
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL2, _y(190), str(job.get('client', '')))
    ty = 204
    c.setFont("Helvetica", 10)
    c.setFillColor(GREY)
    for extra in (job.get('addr1', ''), job.get('addr2', '')):
        if str(extra).strip():
            c.drawString(COL2, _y(ty), str(extra))
            ty += 14

    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(COL2, _y(238), "TERMS")
    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawString(COL2, _y(250), str(job.get('terms') or "Due upon receipt"))
    if str(job.get('due','')).strip():
        c.setFillColor(GREY); c.setFont("Helvetica", 9)
        c.drawString(COL2, _y(262), f"Due {job['due']}")
    if str(job.get('po', '')).strip():
        c.setFillColor(GREY)
        c.setFont("Helvetica", 9)
        c.drawString(COL2, _y(273), f"PO / Ref: {job['po']}")

    # Table header
    c.setFillColor(PINK_BAR)
    c.rect(L, _y(298), R - L, 20, stroke=0, fill=1)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(L + 9, _y(292), "DESCRIPTION")
    c.drawRightString(X_QTY, _y(292), "QTY")
    c.drawRightString(X_RATE, _y(292), "RATE")
    c.drawRightString(X_AMT, _y(292), "AMOUNT")

    qty = float(job.get('qty') or 1)
    rate = float(job.get('rate') or 0)
    amount = qty * rate

    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawString(L + 9, _y(316), str(job.get('description', '')))
    c.drawRightString(X_QTY, _y(316), f"{qty:g}")
    c.drawRightString(X_RATE, _y(316), _money(rate))
    c.drawRightString(X_AMT, _y(316), _money(amount))

    if str(job.get('detail', '')).strip():
        c.setFillColor(GREY)
        c.setFont("Helvetica", 8.5)
        c.drawString(L + 9, _y(329), str(job['detail']))

    c.setStrokeColor(LINE)
    c.setLineWidth(0.5)
    for rule in (334, 360, 386, 412, 438):
        c.line(L, _y(rule), R, _y(rule))

    # Totals
    tax = float(job.get('tax') or 0)
    total = amount + tax

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GREY)
    c.drawString(COL2 + 38, _y(464), "SUBTOTAL")
    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawRightString(X_AMT, _y(464), _money(amount))
    c.setStrokeColor(LINE)
    c.line(COL2 + 38, _y(472), R, _y(472))

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(GREY)
    c.drawString(COL2 + 38, _y(490), "SALES TAX")
    c.setFillColor(DARK)
    c.setFont("Helvetica", 10)
    c.drawRightString(X_AMT, _y(490), _money(tax))
    c.line(COL2 + 38, _y(498), R, _y(498))

    c.setFillColor(PINK_BAR)
    c.rect(COL2 + 30, _y(524), R - (COL2 + 30), 22, stroke=0, fill=1)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(COL2 + 38, _y(518), "TOTAL DUE")
    c.drawRightString(X_AMT, _y(518), _money(total))

    # Payment block
    c.setFillColor(PINK_BAR)
    c.rect(L, _y(600), R - L, 55, stroke=0, fill=1)
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(L + 14, _y(560), "PAYMENT")
    c.setFillColor(DARK)
    c.setFont("Helvetica", 9.5)
    line, lines = "", []
    for wd in _pay_text(job).split():
        trial = (line + " " + wd).strip()
        if c.stringWidth(trial, "Helvetica", 9.5) > (R - L - 28):
            lines.append(line)
            line = wd
        else:
            line = trial
    lines.append(line)
    ty = 575
    for ln in lines:
        c.drawString(L + 14, _y(ty), ln)
        ty += 13

    # Footer
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, _y(632), "Thank you for your business.")
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8)
    c.drawCentredString(W / 2, _y(646),
                        "Family Owned  \u00b7  25+ Years Experience  \u00b7  5.0 Star Rated  \u00b7  Insured & Bonded")
    c.drawCentredString(W / 2, _y(658), "maidinslc.com")

    c.showPage()
    c.save()
    return buf.getvalue()


def build_batch(jobs):
    """List of job dicts -> single merged PDF (needs pypdf)."""
    from pypdf import PdfWriter, PdfReader
    wtr = PdfWriter()
    for j in jobs:
        wtr.append(PdfReader(io.BytesIO(build_invoice(j))))
    out = io.BytesIO()
    wtr.write(out)
    return out.getvalue()
