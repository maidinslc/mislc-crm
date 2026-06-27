"""
Maid In Salt Lake City - Client CRM
A free, hosted Python web app (Streamlit) backed by a Google Sheet.

- If a Google Sheet is connected (via Streamlit secrets), every change saves there
  so your team and your Zapier automations see the same data.
- If nothing is connected yet, the app runs in DEMO mode with sample data so you
  can click around immediately. Connect the sheet whenever you're ready.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime

# ----------------------------------------------------------------------
# Page setup + brand
# ----------------------------------------------------------------------
st.set_page_config(page_title="Maid In SLC — CRM", page_icon="🧼", layout="wide")

PINK = "#F8DFDB"
ROSE = "#C56B64"
st.markdown(f"""
<style>
:root {{ --rose:{ROSE}; }}
.stApp {{ background:#FBF7F6; }}
section[data-testid="stSidebar"] {{ background:#FFFFFF; border-right:1px solid #EEE2DF; }}
h1, h2, h3 {{ font-family:Georgia, 'Times New Roman', serif; color:#2C2422; }}
div[data-testid="stMetric"] {{
    background:#FFFFFF; border:1px solid #EEE2DF; border-radius:16px;
    padding:14px 18px; box-shadow:0 6px 18px rgba(44,36,34,.05);
}}
div[data-testid="stMetricValue"] {{ font-family:Georgia, serif; color:#2C2422; }}
.stButton>button {{
    background:{ROSE}; color:#fff; border:none; border-radius:10px;
    font-weight:600; padding:.5rem 1rem;
}}
.stButton>button:hover {{ background:#A8534D; color:#fff; }}
.brand-bar {{ background:{PINK}; border-radius:14px; padding:14px 20px; margin-bottom:6px; }}
.brand-bar b {{ font-family:Georgia, serif; font-size:18px; color:#2C2422; }}
.badge {{ display:inline-block; padding:3px 10px; border-radius:999px; font-size:12px; font-weight:700; }}
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
FREQ = {"Weekly": 4.33, "Biweekly": 2.17, "Monthly": 1.0, "One-time": 0.0, "Airbnb Turnover": 0.0}
STAGES   = ["Lead", "Quoted", "Active", "Paused", "Lost"]
TYPES    = ["Residential", "Commercial", "Airbnb"]
COUNTIES = ["Salt Lake", "Utah", "Davis", "Summit"]
CLEANERS = ["Carmen", "Adriana", "Either"]
SOURCES  = ["Google", "Instagram", "Referral", "Yelp", "Nextdoor", "Website", "Repeat", "Other"]
REVIEWS  = ["Not asked", "Requested", "Left review"]
REVIEW_LINK = "https://g.page/r/CcekIQhGlVzeEBM/review"

CLIENT_COLS = ["Name", "Type", "Phone", "Email", "Address", "City", "County",
               "Status", "Frequency", "Price", "Cleaner", "Source", "Review", "Notes"]
SERVICE_COLS = ["Date", "Client", "Type", "Cleaner", "Amount", "Paid"]

# ----------------------------------------------------------------------
# Google Sheets layer (with graceful demo fallback)
# ----------------------------------------------------------------------
def get_sheet():
    """Return a gspread Spreadsheet, or None if not configured."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        info = dict(st.secrets["gcp_service_account"])
        scopes = ["https://www.googleapis.com/auth/spreadsheets",
                  "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_info(info, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(st.secrets["sheet_id"])
    except Exception:
        return None

def _ensure_ws(sh, title, cols):
    try:
        ws = sh.worksheet(title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=200, cols=len(cols))
        ws.update([cols])
    return ws

def load_df(sh, title, cols):
    ws = _ensure_ws(sh, title, cols)
    rows = ws.get_all_records()
    df = pd.DataFrame(rows)
    for c in cols:
        if c not in df.columns:
            df[c] = ""
    return df[cols]

def save_df(sh, title, cols, df):
    ws = _ensure_ws(sh, title, cols)
    df = df.fillna("").astype(str)
    ws.clear()
    ws.update([cols] + df[cols].values.tolist())

# ----------------------------------------------------------------------
# Sample data for demo mode
# ----------------------------------------------------------------------
def sample_clients():
    return pd.DataFrame([
        ["Johnson Family","Residential","801-555-0142","kjohnson@email.com","742 Evergreen Ter","Sandy","Salt Lake","Active","Biweekly",140,"Carmen","Google","Not asked","Gate code #4417"],
        ["Park City Loft","Airbnb","435-555-0188","host.pcloft@email.com","210 Main St #5","Park City","Summit","Active","Airbnb Turnover",95,"Adriana","Repeat","Left review","Same-day turnover, 11am checkout"],
        ["Draper Dental Office","Commercial","801-555-0173","office@draperdental.com","1180 E Pioneer Rd","Draper","Salt Lake","Active","Weekly",220,"Either","Referral","Requested","After 6pm only"],
        ["Maria Alvarez","Residential","801-555-0119","malvarez@email.com","388 W 700 S","South Jordan","Salt Lake","Quoted","Monthly",165,"Carmen","Instagram","Not asked","Wants deep clean first"],
        ["Tyler Brooks","Residential","801-555-0166","tbrooks@email.com","55 Inglenook Dr","Midvale","Salt Lake","Lead","One-time",185,"Either","Website","Not asked","Move-out clean, 2BR"],
    ], columns=CLIENT_COLS)

def sample_services():
    def d(n):
        from datetime import timedelta
        return (date.today() - timedelta(days=n)).isoformat()
    return pd.DataFrame([
        [d(2),"Johnson Family","Residential","Carmen",140,"Yes"],
        [d(2),"Park City Loft","Airbnb","Adriana",95,"Yes"],
        [d(4),"Draper Dental Office","Commercial","Either",220,"Yes"],
        [d(9),"Johnson Family","Residential","Carmen",140,"Yes"],
        [d(11),"Draper Dental Office","Commercial","Either",220,"No"],
    ], columns=SERVICE_COLS)

# ----------------------------------------------------------------------
# Load data once into session
# ----------------------------------------------------------------------
sh = get_sheet()
DEMO = sh is None

if "clients" not in st.session_state:
    if DEMO:
        st.session_state.clients = sample_clients()
        st.session_state.services = sample_services()
    else:
        st.session_state.clients = load_df(sh, "Clients", CLIENT_COLS)
        if st.session_state.clients.empty:
            st.session_state.clients = sample_clients()
        st.session_state.services = load_df(sh, "Services", SERVICE_COLS)
        if st.session_state.services.empty:
            st.session_state.services = sample_services()

clients = st.session_state.clients
services = st.session_state.services

def persist():
    if not DEMO:
        save_df(sh, "Clients", CLIENT_COLS, st.session_state.clients)
        save_df(sh, "Services", SERVICE_COLS, st.session_state.services)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def to_num(x):
    try: return float(str(x).replace("$","").replace(",","") or 0)
    except Exception: return 0.0

def monthly_value(row):
    if str(row.get("Status","")) != "Active":
        return 0.0
    return to_num(row.get("Price",0)) * FREQ.get(str(row.get("Frequency","")), 0.0)

def money(n): return "${:,.0f}".format(n or 0)

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="brand-bar">🧼 &nbsp;<b>Maid In SLC</b><br><span style="font-size:11px;letter-spacing:.08em;color:#9A8C8A;text-transform:uppercase;">Client CRM</span></div>', unsafe_allow_html=True)
    page = st.radio("Go to", ["Dashboard", "Clients", "Pipeline", "Service Log"], label_visibility="collapsed")
    st.markdown("---")
    if DEMO:
        st.warning("**Demo mode** — data resets on reload. Connect a Google Sheet to save permanently (see the deploy guide).")
    else:
        st.success("Connected to Google Sheets ✓ Changes save automatically.")

# ----------------------------------------------------------------------
# DASHBOARD
# ----------------------------------------------------------------------
if page == "Dashboard":
    st.title("Dashboard")
    active = (clients["Status"] == "Active").sum()
    pipeline = clients["Status"].isin(["Lead", "Quoted"]).sum()
    mrr = clients.apply(monthly_value, axis=1).sum()
    ym = datetime.now().strftime("%Y-%m")
    svc_month = services[services["Date"].astype(str).str.startswith(ym)]
    rev = svc_month["Amount"].apply(to_num).sum()
    reviews = (clients["Review"] == "Left review").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active clients", int(active), f"{int(pipeline)} in pipeline")
    c2.metric("Est. monthly recurring", money(mrr))
    c3.metric("Revenue this month", money(rev), f"{money(rev*0.2)} your cut")
    c4.metric("Reviews left", int(reviews), "goal: 100")

    st.markdown("### Recent jobs")
    recent = services.sort_values("Date", ascending=False).head(8)
    st.dataframe(recent, use_container_width=True, hide_index=True)

    st.markdown("### Active clients to ask for a review")
    need = clients[(clients["Status"] == "Active") & (clients["Review"] != "Left review")]
    if need.empty:
        st.info("All caught up — every active client has a review.")
    else:
        st.dataframe(need[["Name", "City", "Phone", "Review"]], use_container_width=True, hide_index=True)
        st.caption(f"Review link to text them: {REVIEW_LINK}")

# ----------------------------------------------------------------------
# CLIENTS
# ----------------------------------------------------------------------
elif page == "Clients":
    st.title("Clients")
    col_search, col_s, col_t = st.columns([2, 1, 1])
    q = col_search.text_input("Search", placeholder="Name, city, phone…", label_visibility="collapsed")
    fstat = col_s.selectbox("Status", ["All"] + STAGES, label_visibility="collapsed")
    ftype = col_t.selectbox("Type", ["All"] + TYPES, label_visibility="collapsed")

    view = clients.copy()
    view["Monthly"] = view.apply(monthly_value, axis=1)
    if q:
        mask = view.apply(lambda r: q.lower() in (str(r["Name"])+str(r["City"])+str(r["Phone"])+str(r["Email"])).lower(), axis=1)
        view = view[mask]
    if fstat != "All": view = view[view["Status"] == fstat]
    if ftype != "All": view = view[view["Type"] == ftype]

    st.caption("Edit any cell directly. Add a row at the bottom. Then click **Save changes**.")
    edited = st.data_editor(
        view.drop(columns=["Monthly"]),
        use_container_width=True, hide_index=True, num_rows="dynamic", key="clients_editor",
        column_config={
            "Type":      st.column_config.SelectboxColumn(options=TYPES),
            "County":    st.column_config.SelectboxColumn(options=COUNTIES),
            "Status":    st.column_config.SelectboxColumn(options=STAGES),
            "Frequency": st.column_config.SelectboxColumn(options=list(FREQ.keys())),
            "Cleaner":   st.column_config.SelectboxColumn(options=CLEANERS),
            "Source":    st.column_config.SelectboxColumn(options=SOURCES),
            "Review":    st.column_config.SelectboxColumn(options=REVIEWS),
            "Price":     st.column_config.NumberColumn(format="$%d"),
        },
    )
    if st.button("💾 Save changes", key="save_clients"):
        # Only safe to overwrite wholesale when not filtering/searching
        if q or fstat != "All" or ftype != "All":
            st.warning("Clear the search and filters before saving, so you don't overwrite hidden rows.")
        else:
            st.session_state.clients = edited[CLIENT_COLS].copy()
            persist()
            st.success("Saved." + ("" if not DEMO else " (Demo mode — connect a sheet to keep it.)"))
            st.rerun()

# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------
elif page == "Pipeline":
    st.title("Pipeline")
    st.caption("How many clients sit at each stage, and the recurring value behind them.")
    cols = st.columns(len(STAGES))
    colors = {"Lead":"#E8EFF8","Quoted":"#FBF0DC","Active":"#E7F2E8","Paused":"#EFEAE9","Lost":"#F8E7E6"}
    for col, stage in zip(cols, STAGES):
        items = clients[clients["Status"] == stage]
        val = items.apply(monthly_value, axis=1).sum()
        with col:
            st.markdown(f"**{stage}** &nbsp;<span style='color:#9A8C8A'>{len(items)}</span>", unsafe_allow_html=True)
            if val: st.caption(money(val) + "/mo")
            for _, r in items.iterrows():
                st.markdown(
                    f"<div style='background:{colors[stage]};border-radius:10px;padding:9px 11px;margin-bottom:8px;'>"
                    f"<b style='font-size:13px'>{r['Name']}</b><br>"
                    f"<span style='font-size:11px;color:#6f6360'>{r['Type']} · {r['City']}</span></div>",
                    unsafe_allow_html=True)
            if items.empty:
                st.caption("—")

# ----------------------------------------------------------------------
# SERVICE LOG
# ----------------------------------------------------------------------
elif page == "Service Log":
    st.title("Service Log")
    total = services["Amount"].apply(to_num).sum()
    a, b, c = st.columns(3)
    a.metric("Jobs logged", len(services))
    b.metric("Total billed", money(total))
    c.metric("Your cut (20%)", money(total * 0.2))

    st.caption("Add a row for each completed clean, then click **Save log**.")
    edited = st.data_editor(
        services, use_container_width=True, hide_index=True, num_rows="dynamic", key="svc_editor",
        column_config={
            "Date":    st.column_config.TextColumn(help="YYYY-MM-DD"),
            "Client":  st.column_config.SelectboxColumn(options=sorted(clients["Name"].dropna().unique().tolist())),
            "Type":    st.column_config.SelectboxColumn(options=TYPES),
            "Cleaner": st.column_config.SelectboxColumn(options=CLEANERS),
            "Amount":  st.column_config.NumberColumn(format="$%d"),
            "Paid":    st.column_config.SelectboxColumn(options=["Yes", "No"]),
        },
    )
    if st.button("💾 Save log", key="save_svc"):
        st.session_state.services = edited[SERVICE_COLS].copy()
        persist()
        st.success("Saved." + ("" if not DEMO else " (Demo mode — connect a sheet to keep it.)"))
        st.rerun()
