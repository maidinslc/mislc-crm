"""
calendar_sync.py — Maid In Salt Lake City
Reads jobs off the business Google Calendar so they can be logged
into the Service Log without retyping.

Setup (one time):
  1. Google Cloud console -> enable "Google Calendar API" on the MISLC CRM project
  2. Google Calendar -> the business calendar -> Settings and sharing
     -> Share with specific people -> add crm-bot@mislc-crm.iam.gserviceaccount.com
     -> permission "See all event details"
  3. Same settings page, scroll to "Integrate calendar" -> copy the Calendar ID
  4. Streamlit secrets:  calendar_id = "....@group.calendar.google.com"

Requires: google-api-python-client
"""

import re
from datetime import datetime, timezone
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _service(sa_info):
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


def fetch_events(sa_info, calendar_id, start_date, end_date):
    """Return a list of dicts: date, title, start, end, unit, duration_hrs."""
    svc = _service(sa_info)
    t_min = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
    t_max = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"

    res = svc.events().list(calendarId=calendar_id, timeMin=t_min, timeMax=t_max,
                            singleEvents=True, orderBy="startTime",
                            maxResults=250).execute()

    out = []
    for e in res.get("items", []):
        title = (e.get("summary") or "(no title)").strip()
        s = e["start"].get("dateTime") or e["start"].get("date")
        f = e["end"].get("dateTime") or e["end"].get("date")
        allday = "dateTime" not in e["start"]

        day = s[:10]
        hrs = 0.0
        stime = etime = ""
        if not allday:
            try:
                sd = datetime.fromisoformat(s); ed = datetime.fromisoformat(f)
                hrs = round((ed - sd).total_seconds() / 3600, 2)
                stime = sd.strftime("%-I:%M %p") if hasattr(sd, "strftime") else ""
                etime = ed.strftime("%-I:%M %p")
            except Exception:
                pass

        m = re.search(r"#\s*(\w+)", title)
        out.append({"date": day, "title": title, "start": stime, "end": etime,
                    "unit": m.group(1) if m else "", "hours": hrs,
                    "id": e.get("id", ""), "location": e.get("location", "")})
    return out


def guess_client(title, client_names):
    """Best-effort match of an event title to a known client name."""
    t = re.sub(r"[^a-z ]", " ", title.lower())
    best, score = "", 0
    for name in client_names:
        words = [w for w in re.sub(r"[^a-z ]", " ", str(name).lower()).split() if len(w) > 3]
        if not words:
            continue
        hit = sum(1 for w in words if w in t)
        if hit > score:
            best, score = name, hit
    return best if score else ""
