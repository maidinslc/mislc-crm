"""
drive_archive.py — Maid In Salt Lake City
Saves every invoice PDF to a Google Drive folder, filed by year.

Setup (one time):
  1. Google Cloud console -> enable "Google Drive API" (already on if Sheets works)
  2. Google Drive -> create a folder called "Maid In Salt Lake City — Invoices"
  3. Share that folder with crm-bot@mislc-crm.iam.gserviceaccount.com as Editor
  4. Open the folder; the URL ends in the folder ID -> Streamlit secrets:
         drive_folder_id = "1AbC..."

Service accounts have no storage of their own, so the folder must be owned by
your account and shared with the bot. Files land in your Drive, under your quota.
"""

import io
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def _svc(sa_info):
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def _subfolder(svc, parent_id, name):
    """Find or create a subfolder by name."""
    q = (f"name='{name}' and '{parent_id}' in parents and "
         "mimeType='application/vnd.google-apps.folder' and trashed=false")
    hit = svc.files().list(q=q, fields="files(id)", pageSize=1).execute().get("files", [])
    if hit:
        return hit[0]["id"]
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id]}
    return svc.files().create(body=meta, fields="id").execute()["id"]


def archive_invoice(sa_info, folder_id, filename, pdf_bytes, year=None, client=None):
    """Upload a PDF into <folder>/<year>/<client>/. Returns a shareable link."""
    svc = _svc(sa_info)
    parent = folder_id
    if year:
        parent = _subfolder(svc, parent, str(year))
    if client:
        safe = "".join(ch for ch in str(client) if ch.isalnum() or ch in " &-").strip()
        parent = _subfolder(svc, parent, safe[:60] or "Unfiled")

    # replace an existing file of the same name so re-issuing doesn't duplicate
    q = f"name='{filename}' and '{parent}' in parents and trashed=false"
    old = svc.files().list(q=q, fields="files(id)", pageSize=1).execute().get("files", [])
    media = MediaIoBaseUpload(io.BytesIO(pdf_bytes), mimetype="application/pdf",
                              resumable=False)
    if old:
        f = svc.files().update(fileId=old[0]["id"], media_body=media,
                               fields="id,webViewLink").execute()
    else:
        f = svc.files().create(body={"name": filename, "parents": [parent]},
                               media_body=media, fields="id,webViewLink").execute()
    return f.get("webViewLink", "")
