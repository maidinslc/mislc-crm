"""
square_sync.py — Maid In Salt Lake City
Reads recent Square payments so invoices can be marked paid without
reconciling by hand.

Setup (one time):
  1. developer.squareup.com -> sign in with your Square account
  2. Applications -> your app (or create one) -> Credentials
  3. Copy the PRODUCTION Access Token
  4. Streamlit secrets:

        [square]
        access_token = "EAAA..."
        environment = "production"     # or "sandbox" for testing

Read-only: this module never moves money, it only lists completed payments.
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

BASE = {"production": "https://connect.squareup.com",
        "sandbox": "https://connect.squareupsandbox.com"}


def fetch_payments(access_token, days_back=60, environment="production"):
    """Return completed payments as [{date, amount, note, id, status}]."""
    begin = (datetime.utcnow() - timedelta(days=days_back)).isoformat("T") + "Z"
    qs = urllib.parse.urlencode({"begin_time": begin, "sort_order": "DESC", "limit": 100})
    url = f"{BASE.get(environment, BASE['production'])}/v2/payments?{qs}"

    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {access_token}",
        "Square-Version": "2025-01-23",
        "Content-Type": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.loads(r.read().decode())

    out = []
    for p in data.get("payments", []):
        if p.get("status") != "COMPLETED":
            continue
        amt = p.get("amount_money", {})
        out.append({
            "id": p.get("id", ""),
            "date": (p.get("created_at", "") or "")[:10],
            "amount": round(amt.get("amount", 0) / 100.0, 2),
            "note": p.get("note", "") or "",
            "source": (p.get("source_type", "") or "").title(),
        })
    return out


def match_payments(payments, invoices_df, to_num, window_days=45):
    """
    Suggest payment -> invoice pairings for unpaid invoices.
    Matches on exact total, then nearest date within the window.
    Returns [(payment, invoice_index, invoice_row)].
    """
    open_inv = invoices_df[invoices_df["Status"] != "Paid"]
    used, pairs = set(), []
    for p in payments:
        best, best_gap = None, None
        for i, r in open_inv.iterrows():
            if i in used:
                continue
            total = to_num(r["Amount"]) + to_num(r.get("Tax", 0))
            if abs(total - p["amount"]) > 0.005:
                continue
            try:
                gap = abs((datetime.fromisoformat(p["date"])
                           - datetime.fromisoformat(str(r["Date"])[:10])).days)
            except Exception:
                gap = 999
            if gap > window_days:
                continue
            if best_gap is None or gap < best_gap:
                best, best_gap = (i, r), gap
        if best:
            used.add(best[0])
            pairs.append((p, best[0], best[1]))
    return pairs
