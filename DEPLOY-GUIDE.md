# Putting your CRM online — free, with Python

This turns the CRM into a real web app at its own link (like
`https://maid-in-slc-crm.streamlit.app`) that you can open on your phone or
computer. It runs on **Streamlit Community Cloud**, which is free.

You'll do it in two parts:

- **Part A** gets the app live in about 5 minutes. It works right away in "demo mode" — you can click everything, but data resets when you reload.
- **Part B** connects a Google Sheet so every change saves for good and your team (and Zapier) see the same data.

Do Part A first. Do Part B whenever you're ready — the app keeps working in between.

---

## What's in this folder

```
mislc-crm/
├── streamlit_app.py              ← the app
├── requirements.txt              ← the Python pieces it needs
├── .gitignore
└── .streamlit/
    ├── config.toml               ← the pink theme
    └── secrets.toml.EXAMPLE      ← template for Part B (don't upload the real one)
```

You don't need to edit any code. Just upload these files.

---

## PART A — Get it live (≈5 minutes)

### 1. Make a free GitHub account
Go to **github.com** and sign up. GitHub is just where your app's files live online. Free.

### 2. Create a place for the files
- Click the **+** in the top-right of GitHub → **New repository**.
- Name it `mislc-crm`. Leave it **Public**. Click **Create repository**.
- On the next page, click **uploading an existing file**.
- Drag in `streamlit_app.py` and `requirements.txt`.
- Then drag in the `.streamlit` folder (or upload `config.toml` into a folder you name `.streamlit`).
- Click **Commit changes**.

> Do **not** upload `secrets.toml.EXAMPLE` content as real secrets, and never upload a real `secrets.toml`. That's only for Part B, and it goes in Streamlit's settings, not GitHub.

### 3. Deploy it
- Go to **share.streamlit.io** and click **Continue with GitHub** to sign in.
- Click **Create app** → **"Yup, I have an app."**
- Fill in:
  - **Repository:** `your-username/mislc-crm`
  - **Branch:** `main`
  - **Main file path:** `streamlit_app.py`
  - **App URL:** pick something like `maid-in-slc-crm` (this becomes your link).
- Click **Deploy**. Give it 1–3 minutes.

That's it. You now have a live link. Open it on your phone, then use your browser's
**Share → Add to Home Screen** to get a tappable icon. The sidebar will say
*"Demo mode"* until you finish Part B.

---

## PART B — Make it save to a Google Sheet

This is the only fiddly part. Take it slow; it's a one-time setup.

### 1. Make the sheet
- Create a new Google Sheet (call it "Maid In SLC CRM").
- Copy its **ID** from the address bar — it's the long code between `/d/` and `/edit`:
  `docs.google.com/spreadsheets/d/`**`THIS_LONG_PART`**`/edit`
- Keep it handy. (The app makes the "Clients" and "Services" tabs for you.)

### 2. Turn on the Google APIs
- Go to **console.cloud.google.com**.
- Top bar → **Select a project** → **New Project** → name it `mislc-crm` → **Create**.
- In the search bar, search **Google Sheets API** → open it → **Enable**.
- Search **Google Drive API** → open it → **Enable**.

### 3. Make a "service account" (a robot login for the app)
- Left menu → **APIs & Services → Credentials**.
- **+ Create Credentials → Service account**.
- Give it a name like `crm-bot` → **Create and Continue** → **Done**.
- Click the service account you just made → **Keys** tab → **Add Key → Create new key → JSON → Create**.
- A `.json` file downloads. **This is the password file — keep it private.**

### 4. Give the robot access to your sheet
- Open that downloaded `.json` file in any text editor.
- Find the line `"client_email": "crm-bot@....iam.gserviceaccount.com"` and copy that email.
- Open your Google Sheet → **Share** → paste that email → set to **Editor** → **Send**.

### 5. Hand the keys to Streamlit
- In Streamlit Cloud, open your app → **⋮ menu → Settings → Secrets**.
- Open `secrets.toml.EXAMPLE` (in this folder) to see the exact layout.
- Paste in this shape, filling values **from your downloaded JSON file**:

```toml
sheet_id = "THE_LONG_ID_FROM_STEP_1"

[gcp_service_account]
type = "service_account"
project_id = "...from JSON..."
private_key_id = "...from JSON..."
private_key = "-----BEGIN PRIVATE KEY-----\n...from JSON...\n-----END PRIVATE KEY-----\n"
client_email = "...from JSON..."
client_id = "...from JSON..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "...from JSON..."
```

> Copy `private_key` exactly as it appears in the JSON, keeping the `\n` bits. They matter.

- Click **Save**. The app reboots.

### 6. Done
The sidebar should now say **"Connected to Google Sheets ✓."** Add or edit a client,
hit **Save**, and watch the row appear in your Google Sheet. Your team can open that
same sheet, and your Zapier automations can run off it.

---

## Keeping it private (optional)
On a free public Streamlit app, anyone with the link can view it. To lock it down:
**app Settings → Sharing → "Only specific people can view this app,"** then add the
Google email addresses for you and your cleaners.

---

## If something breaks
- **"Demo mode" won't go away:** a secret value is slightly off. Re-check `sheet_id` and that `private_key` kept its `\n` line breaks.
- **"SpreadsheetNotFound":** you forgot Step 4 — share the sheet with the robot's `client_email`.
- **App won't start:** open the app's **logs** (lower-right on the app page) to see the error line.

---

## Honest note
This Python route is the most "real app" version, but it's also the most setup. If you
ever decide the Google Sheet alone is enough, the spreadsheet CRM I built does the same
job with zero deployment — and a no-code tool like **Google AppSheet** or **Glide** can
turn that very sheet into a phone app in minutes without any of Part B. The choice is
just how much polish vs. setup you want.
