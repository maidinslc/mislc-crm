"""
Maid In Salt Lake City — Client CRM
Free, hosted Python web app (Streamlit) with an optional Google Sheet backend.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta

# ----------------------------------------------------------------------
# Page + theme
# ----------------------------------------------------------------------
st.set_page_config(page_title="Maid In Salt Lake City — CRM", page_icon="🧼", layout="wide")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{ --pink:#F8DFDB; --pink-wash:#FCEFEC; --rose:#C56B64; --rose-dk:#A8534D;
  --ink:#2C2422; --muted:#9A8C8A; --line:#EEE2DF; --paper:#FFFFFF; --bg:#FBF7F6;
  --green:#2E7D32; --green-bg:#E7F2E8; --amber:#B7791F; --amber-bg:#FBF0DC;
  --blue:#3F6FB5; --blue-bg:#E8EFF8; --grey:#7E7472; --grey-bg:#EFEAE9;
  --red:#C0504D; --red-bg:#F8E7E6; }

.stApp{ background:var(--bg); }
html, body, [class*="css"]{ font-family:'Inter',system-ui,sans-serif; color:var(--ink); }
.block-container{ padding-top:1.4rem; max-width:1180px; }
#MainMenu, footer, header[data-testid="stHeader"]{ visibility:hidden; }

/* Sidebar */
section[data-testid="stSidebar"]{ background:var(--paper); border-right:1px solid var(--line); }
.side-brand{ display:flex; gap:11px; align-items:center; padding:6px 4px 4px; }
.side-brand .mk{ width:40px;height:40px;border-radius:12px;background:var(--pink);
  display:grid;place-items:center;font-size:20px;flex-shrink:0; }
.side-brand .nm{ font-family:'Fraunces',serif; font-weight:600; font-size:15px; line-height:1.15; color:var(--ink); }
.side-brand .nm small{ display:block; font-family:'Inter'; font-weight:600; font-size:10px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--muted); margin-top:3px; }

/* Page header */
.page-h{ font-family:'Fraunces',serif !important; font-weight:600 !important; font-size:30px !important;
  color:var(--ink) !important; margin:2px 0 2px !important; letter-spacing:-.01em; }
.page-sub{ color:var(--muted); font-size:14px; margin:0 0 22px; }
.sec-h{ font-family:'Fraunces',serif; font-weight:600; font-size:18px; color:var(--ink);
  margin:26px 0 12px; }

/* KPI cards */
.kpis{ display:grid; grid-template-columns:repeat(4,1fr); gap:14px; }
@media(max-width:820px){ .kpis{ grid-template-columns:repeat(2,1fr);} }
.kpi{ background:var(--paper); border:1px solid var(--line); border-radius:18px; padding:18px 20px;
  box-shadow:0 1px 2px rgba(44,36,34,.04),0 10px 26px rgba(44,36,34,.05); position:relative; overflow:hidden; }
.kpi:before{ content:""; position:absolute; top:0; left:0; right:0; height:3px; background:var(--pink); }
.kpi.g:before{ background:var(--green);} .kpi.a:before{ background:var(--amber);}
.kpi .l{ font-size:11.5px; font-weight:700; letter-spacing:.05em; text-transform:uppercase; color:var(--muted); }
.kpi .v{ font-family:'Fraunces',serif; font-weight:600; font-size:34px; color:var(--ink); line-height:1.05; margin-top:10px; letter-spacing:-.02em; }
.kpi .s{ font-size:12.5px; color:var(--muted); margin-top:5px; }
.kpi .s b{ color:var(--green); font-weight:600; }

/* Generic card / table */
.card{ background:var(--paper); border:1px solid var(--line); border-radius:18px;
  box-shadow:0 1px 2px rgba(44,36,34,.04),0 10px 26px rgba(44,36,34,.05); overflow:hidden; }
table.t{ width:100%; border-collapse:collapse; font-size:13.5px; }
table.t th{ text-align:left; padding:12px 18px; font-size:11px; letter-spacing:.05em; text-transform:uppercase;
  color:var(--muted); font-weight:700; background:var(--bg); border-bottom:1px solid var(--line); }
table.t td{ padding:13px 18px; border-bottom:1px solid var(--line); color:var(--ink); }
table.t tr:last-child td{ border-bottom:none; }
table.t td.r, table.t th.r{ text-align:right; }

/* pills + badges */
.pill{ display:inline-block; padding:3px 11px; border-radius:999px; font-size:12px; font-weight:700; }
.pill.Active{ background:var(--green-bg); color:var(--green);} .pill.Quoted{ background:var(--amber-bg); color:var(--amber);}
.pill.Lead{ background:var(--blue-bg); color:var(--blue);} .pill.Paused{ background:var(--grey-bg); color:var(--grey);}
.pill.Lost{ background:var(--red-bg); color:var(--red);} .pill.Yes{ background:var(--green-bg); color:var(--green);}
.pill.No{ background:var(--red-bg); color:var(--red);}
.badge{ display:inline-block; padding:3px 10px; border-radius:8px; font-size:11.5px; font-weight:700;
  background:var(--pink-wash); color:var(--rose-dk); }

/* client card */
.clist{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }
@media(max-width:820px){ .clist{ grid-template-columns:1fr; } }
.cc{ background:var(--paper); border:1px solid var(--line); border-radius:16px; padding:15px 17px;
  box-shadow:0 1px 2px rgba(44,36,34,.04); }
.cc .top{ display:flex; justify-content:space-between; align-items:flex-start; gap:10px; }
.cc .nm{ font-weight:700; font-size:15px; color:var(--ink); }
.cc .meta{ font-size:12.5px; color:var(--muted); margin-top:3px; }
.cc .row{ display:flex; gap:8px; align-items:center; margin-top:12px; flex-wrap:wrap; }
.cc .mv{ margin-left:auto; font-weight:700; color:var(--ink); font-size:14px; }
.lnk{ display:inline-flex; align-items:center; gap:5px; padding:6px 11px; border-radius:9px; font-size:12.5px;
  font-weight:600; background:var(--pink-wash); color:var(--rose-dk); text-decoration:none; }
.lnk:hover{ background:var(--pink); }

/* pipeline */
.board{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; }
@media(max-width:900px){ .board{ grid-template-columns:repeat(2,1fr);} }
.col{ background:var(--paper); border:1px solid var(--line); border-radius:14px; padding:12px; }
.col .ch{ display:flex; justify-content:space-between; align-items:center; font-size:13px; font-weight:700; margin-bottom:4px; }
.col .ch .c{ color:var(--muted); font-weight:600; }
.col .cv{ font-size:11.5px; color:var(--muted); margin-bottom:10px; }
.pc{ border-radius:11px; padding:10px 12px; margin-bottom:8px; }
.pc b{ font-size:13px; } .pc span{ font-size:11px; color:#6f6360; display:block; margin-top:2px; }

/* Buttons + inputs */
.stButton>button{ background:var(--rose); color:#fff; border:none; border-radius:11px; font-weight:600; padding:.5rem 1.1rem; }
.stButton>button:hover{ background:var(--rose-dk); color:#fff; }
div[data-testid="stTextInput"] input, div[data-baseweb="select"]>div{ border-radius:11px !important; }
.stForm{ background:var(--paper); border:1px solid var(--line)!important; border-radius:18px; padding:6px 6px 0; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------
FREQ = {"Weekly":4.33,"Biweekly":2.17,"Monthly":1.0,"One-time":0.0,"Airbnb Turnover":0.0}
STAGES=["Lead","Quoted","Active","Paused","Lost"]; TYPES=["Residential","Commercial","Airbnb"]
COUNTIES=["Salt Lake","Utah","Davis","Summit"]; CLEANERS=["Carmen","Adriana","Either"]
SOURCES=["Google","Instagram","Referral","Yelp","Nextdoor","Website","Repeat","Other"]
REVIEWS=["Not asked","Requested","Left review"]
REVIEW_LINK="https://g.page/r/CcekIQhGlVzeEBM/review"
CLIENT_COLS=["Name","Type","Phone","Email","Address","City","County","Status","Frequency","Price","Cleaner","Source","Review","Notes"]
SERVICE_COLS=["Date","Client","Type","Cleaner","Amount","Paid"]

# ----------------------------------------------------------------------
# Google Sheets backend (demo fallback)
# ----------------------------------------------------------------------
def get_sheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        info=dict(st.secrets["gcp_service_account"])
        creds=Credentials.from_service_account_info(info, scopes=[
            "https://www.googleapis.com/auth/spreadsheets","https://www.googleapis.com/auth/drive"])
        return gspread.authorize(creds).open_by_key(st.secrets["sheet_id"])
    except Exception:
        return None

def _ws(sh,title,cols):
    try: ws=sh.worksheet(title)
    except Exception:
        ws=sh.add_worksheet(title=title,rows=300,cols=len(cols)); ws.update([cols])
    return ws
def load_df(sh,title,cols):
    df=pd.DataFrame(_ws(sh,title,cols).get_all_records())
    for c in cols:
        if c not in df.columns: df[c]=""
    return df[cols]
def save_df(sh,title,cols,df):
    ws=_ws(sh,title,cols); df=df.fillna("").astype(str); ws.clear(); ws.update([cols]+df[cols].values.tolist())

def sample_clients():
    return pd.DataFrame([
        ["Johnson Family","Residential","801-555-0142","kjohnson@email.com","742 Evergreen Ter","Sandy","Salt Lake","Active","Biweekly",140,"Carmen","Google","Not asked","Gate code #4417"],
        ["Park City Loft","Airbnb","435-555-0188","host.pcloft@email.com","210 Main St #5","Park City","Summit","Active","Airbnb Turnover",95,"Adriana","Repeat","Left review","Same-day turnover, 11am"],
        ["Draper Dental Office","Commercial","801-555-0173","office@draperdental.com","1180 E Pioneer Rd","Draper","Salt Lake","Active","Weekly",220,"Either","Referral","Requested","After 6pm only"],
        ["Maria Alvarez","Residential","801-555-0119","malvarez@email.com","388 W 700 S","South Jordan","Salt Lake","Quoted","Monthly",165,"Carmen","Instagram","Not asked","Wants deep clean first"],
        ["Tyler Brooks","Residential","801-555-0166","tbrooks@email.com","55 Inglenook Dr","Midvale","Salt Lake","Lead","One-time",185,"Either","Website","Not asked","Move-out clean, 2BR"],
    ], columns=CLIENT_COLS)
def sample_services():
    d=lambda n:(date.today()-timedelta(days=n)).isoformat()
    return pd.DataFrame([
        [d(2),"Johnson Family","Residential","Carmen",140,"Yes"],[d(2),"Park City Loft","Airbnb","Adriana",95,"Yes"],
        [d(4),"Draper Dental Office","Commercial","Either",220,"Yes"],[d(9),"Johnson Family","Residential","Carmen",140,"Yes"],
        [d(11),"Draper Dental Office","Commercial","Either",220,"No"],
    ], columns=SERVICE_COLS)

sh=get_sheet(); DEMO=sh is None
if "clients" not in st.session_state:
    if DEMO:
        st.session_state.clients=sample_clients(); st.session_state.services=sample_services()
    else:
        st.session_state.clients=load_df(sh,"Clients",CLIENT_COLS)
        if st.session_state.clients.empty: st.session_state.clients=sample_clients()
        st.session_state.services=load_df(sh,"Services",SERVICE_COLS)
        if st.session_state.services.empty: st.session_state.services=sample_services()
clients=st.session_state.clients; services=st.session_state.services
def persist():
    if not DEMO:
        save_df(sh,"Clients",CLIENT_COLS,st.session_state.clients)
        save_df(sh,"Services",SERVICE_COLS,st.session_state.services)

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def to_num(x):
    try: return float(str(x).replace("$","").replace(",","") or 0)
    except Exception: return 0.0
def monthly_value(r):
    return 0.0 if str(r.get("Status",""))!="Active" else to_num(r.get("Price",0))*FREQ.get(str(r.get("Frequency","")),0.0)
def money(n): return "${:,.0f}".format(n or 0)
def digits(p): return "".join(ch for ch in str(p) if ch.isdigit() or ch=="+")
def esc(x):
    return (str(x) if x is not None else "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

# ----------------------------------------------------------------------
# Sidebar
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="side-brand"><div class="mk">🧼</div><div class="nm">Maid In Salt Lake City'
                '<small>Client CRM</small></div></div>', unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    page=st.radio("Navigate", ["Dashboard","Clients","Pipeline","Service Log"], label_visibility="collapsed")
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    if DEMO:
        st.warning("**Demo mode** — changes reset on reload. Connect a Google Sheet to save (see the deploy guide).")
    else:
        st.success("Saving to Google Sheets ✓")

def header(title, sub):
    st.markdown(f"<div class='page-h'>{title}</div><div class='page-sub'>{sub}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# DASHBOARD
# ----------------------------------------------------------------------
if page=="Dashboard":
    header("Dashboard", "Your business at a glance.")
    active=int((clients["Status"]=="Active").sum())
    pipeline=int(clients["Status"].isin(["Lead","Quoted"]).sum())
    mrr=clients.apply(monthly_value,axis=1).sum()
    ym=datetime.now().strftime("%Y-%m")
    rev=services[services["Date"].astype(str).str.startswith(ym)]["Amount"].apply(to_num).sum()
    reviews=int((clients["Review"]=="Left review").sum())
    st.markdown(f"""<div class="kpis">
      <div class="kpi"><div class="l">Active clients</div><div class="v">{active}</div><div class="s">{pipeline} in pipeline</div></div>
      <div class="kpi g"><div class="l">Est. monthly recurring</div><div class="v">{money(mrr)}</div><div class="s">from active recurring</div></div>
      <div class="kpi g"><div class="l">Revenue this month</div><div class="v">{money(rev)}</div><div class="s"><b>{money(rev*0.2)}</b> your cut</div></div>
      <div class="kpi a"><div class="l">Reviews left</div><div class="v">{reviews}</div><div class="s">goal: 100</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-h'>Recent jobs</div>", unsafe_allow_html=True)
    recent=services.sort_values("Date",ascending=False).head(6)
    rows="".join(f"<tr><td>{esc(r['Date'])}</td><td><b>{esc(r['Client'])}</b></td><td>{esc(r['Cleaner'])}</td>"
                 f"<td><span class='pill {'Yes' if str(r['Paid'])=='Yes' else 'No'}'>{esc(r['Paid'])}</span></td>"
                 f"<td class='r'><b>{money(to_num(r['Amount']))}</b></td></tr>" for _,r in recent.iterrows())
    st.markdown(f"<div class='card'><table class='t'><tr><th>Date</th><th>Client</th><th>Cleaner</th><th>Paid</th><th class='r'>Amount</th></tr>{rows}</table></div>", unsafe_allow_html=True)

    need=clients[(clients["Status"]=="Active")&(clients["Review"]!="Left review")]
    st.markdown("<div class='sec-h'>Ask these clients for a review</div>", unsafe_allow_html=True)
    if need.empty:
        st.markdown("<div class='card' style='padding:18px'>All caught up — every active client has a review. 🎉</div>", unsafe_allow_html=True)
    else:
        body="".join(
            f"<div class='cc'><div class='top'><div><div class='nm'>{esc(r['Name'])}</div>"
            f"<div class='meta'>{esc(r['City'])} · {esc(r['Review'])}</div></div></div>"
            f"<div class='row'><a class='lnk' href='sms:{digits(r['Phone'])}?&body={'Thanks for choosing Maid In Salt Lake City! Would you mind leaving us a quick review? '+REVIEW_LINK}'>★ Text review link</a></div></div>"
            for _,r in need.iterrows())
        st.markdown(f"<div class='clist'>{body}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CLIENTS
# ----------------------------------------------------------------------
elif page=="Clients":
    header("Clients", f"{len(clients)} total · {int((clients['Status']=='Active').sum())} active")
    c1,c2,c3=st.columns([2,1,1])
    q=c1.text_input("Search",placeholder="Search name, city, phone…",label_visibility="collapsed")
    fs=c2.selectbox("Status",["All"]+STAGES,label_visibility="collapsed")
    ft=c3.selectbox("Type",["All"]+TYPES,label_visibility="collapsed")

    view=clients.copy()
    if q:
        m=view.apply(lambda r:q.lower() in (str(r['Name'])+str(r['City'])+str(r['Phone'])+str(r['Email'])).lower(),axis=1)
        view=view[m]
    if fs!="All": view=view[view["Status"]==fs]
    if ft!="All": view=view[view["Type"]==ft]

    if view.empty:
        st.markdown("<div class='card' style='padding:22px'>No clients match. Clear the search/filters, or add one below.</div>", unsafe_allow_html=True)
    else:
        cards="".join(
            f"<div class='cc'><div class='top'><div><div class='nm'>{esc(r['Name'])}</div>"
            f"<div class='meta'>{esc(r['City'])}{' · '+esc(r['County'])+' Co.' if r['County'] else ''}</div></div>"
            f"<span class='pill {esc(r['Status'])}'>{esc(r['Status'])}</span></div>"
            f"<div class='row'><span class='badge'>{esc(r['Type'])}</span>"
            f"<span class='meta'>{esc(r['Frequency'])}</span>"
            f"<span class='mv'>{money(monthly_value(r)) if monthly_value(r) else '—'}</span></div>"
            f"<div class='row'><a class='lnk' href='tel:{digits(r['Phone'])}'>📞 Call</a>"
            f"<a class='lnk' href='sms:{digits(r['Phone'])}'>💬 Text</a>"
            f"<a class='lnk' href='mailto:{esc(r['Email'])}'>✉ Email</a></div></div>"
            for _,r in view.iterrows())
        st.markdown(f"<div class='clist'>{cards}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sec-h'>Add a client</div>", unsafe_allow_html=True)
    with st.form("add_client", clear_on_submit=True):
        a,b=st.columns(2)
        name=a.text_input("Name"); typ=b.selectbox("Type",TYPES)
        a2,b2=st.columns(2); phone=a2.text_input("Phone"); email=b2.text_input("Email")
        addr=st.text_input("Address")
        a3,b3=st.columns(2); city=a3.text_input("City"); county=b3.selectbox("County",COUNTIES)
        a4,b4=st.columns(2); status=a4.selectbox("Status",STAGES,index=0); freq=b4.selectbox("Frequency",list(FREQ.keys()),index=1)
        a5,b5=st.columns(2); price=a5.number_input("Price / clean ($)",min_value=0,step=5); cleaner=b5.selectbox("Cleaner",CLEANERS,index=2)
        a6,b6=st.columns(2); source=a6.selectbox("Source",SOURCES); review=b6.selectbox("Review",REVIEWS)
        notes=st.text_area("Notes")
        if st.form_submit_button("➕ Add client"):
            if not name.strip():
                st.warning("Add a name first.")
            else:
                new=pd.DataFrame([[name,typ,phone,email,addr,city,county,status,freq,price,cleaner,source,review,notes]],columns=CLIENT_COLS)
                st.session_state.clients=pd.concat([st.session_state.clients,new],ignore_index=True)
                persist(); st.success(f"Added {name}."); st.rerun()

    if len(clients):
        with st.expander("✏️  Edit or remove a client"):
            labels=[f"{r['Name']} — {r['City']}" for _,r in clients.iterrows()]
            pick=st.selectbox("Choose client",range(len(labels)),format_func=lambda i:labels[i])
            r=clients.iloc[pick]
            with st.form("edit_client"):
                a,b=st.columns(2)
                name=a.text_input("Name",r["Name"]); typ=b.selectbox("Type",TYPES,index=TYPES.index(r["Type"]) if r["Type"] in TYPES else 0)
                a2,b2=st.columns(2); phone=a2.text_input("Phone",r["Phone"]); email=b2.text_input("Email",r["Email"])
                addr=st.text_input("Address",r["Address"])
                a3,b3=st.columns(2); city=a3.text_input("City",r["City"]); county=b3.selectbox("County",COUNTIES,index=COUNTIES.index(r["County"]) if r["County"] in COUNTIES else 0)
                a4,b4=st.columns(2); status=a4.selectbox("Status",STAGES,index=STAGES.index(r["Status"]) if r["Status"] in STAGES else 0)
                freq=b4.selectbox("Frequency",list(FREQ.keys()),index=list(FREQ.keys()).index(r["Frequency"]) if r["Frequency"] in FREQ else 1)
                a5,b5=st.columns(2); price=a5.number_input("Price / clean ($)",min_value=0,step=5,value=int(to_num(r["Price"]))); cleaner=b5.selectbox("Cleaner",CLEANERS,index=CLEANERS.index(r["Cleaner"]) if r["Cleaner"] in CLEANERS else 2)
                a6,b6=st.columns(2); source=a6.selectbox("Source",SOURCES,index=SOURCES.index(r["Source"]) if r["Source"] in SOURCES else 0); review=b6.selectbox("Review",REVIEWS,index=REVIEWS.index(r["Review"]) if r["Review"] in REVIEWS else 0)
                notes=st.text_area("Notes",r["Notes"])
                s1,s2=st.columns(2)
                if s1.form_submit_button("💾 Save changes"):
                    st.session_state.clients.iloc[pick]=[name,typ,phone,email,addr,city,county,status,freq,price,cleaner,source,review,notes]
                    persist(); st.success("Saved."); st.rerun()
                if s2.form_submit_button("🗑 Delete client"):
                    st.session_state.clients=st.session_state.clients.drop(st.session_state.clients.index[pick]).reset_index(drop=True)
                    persist(); st.success("Deleted."); st.rerun()

# ----------------------------------------------------------------------
# PIPELINE
# ----------------------------------------------------------------------
elif page=="Pipeline":
    header("Pipeline", "How many clients sit at each stage, and the recurring value behind them.")
    bg={"Lead":"var(--blue-bg)","Quoted":"var(--amber-bg)","Active":"var(--green-bg)","Paused":"var(--grey-bg)","Lost":"var(--red-bg)"}
    cols=""
    for s in STAGES:
        items=clients[clients["Status"]==s]; val=items.apply(monthly_value,axis=1).sum()
        cards="".join(f"<div class='pc' style='background:{bg[s]}'><b>{esc(r['Name'])}</b>"
                      f"<span>{esc(r['Type'])} · {esc(r['City'])}</span></div>" for _,r in items.iterrows())
        if items.empty: cards="<div class='cv'>—</div>"
        cols+=(f"<div class='col'><div class='ch'>{s}<span class='c'>{len(items)}</span></div>"
               f"<div class='cv'>{money(val)+'/mo' if val else '&nbsp;'}</div>{cards}</div>")
    st.markdown(f"<div class='board'>{cols}</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SERVICE LOG
# ----------------------------------------------------------------------
elif page=="Service Log":
    header("Service Log", "Every completed clean, and what you keep.")
    total=services["Amount"].apply(to_num).sum()
    st.markdown(f"""<div class="kpis" style="grid-template-columns:repeat(3,1fr)">
      <div class="kpi"><div class="l">Jobs logged</div><div class="v">{len(services)}</div></div>
      <div class="kpi g"><div class="l">Total billed</div><div class="v">{money(total)}</div></div>
      <div class="kpi a"><div class="l">Your cut (20%)</div><div class="v">{money(total*0.2)}</div></div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<div class='sec-h'>Log a job</div>", unsafe_allow_html=True)
    with st.form("add_job", clear_on_submit=True):
        a,b=st.columns(2)
        jdate=a.date_input("Date",value=date.today())
        names=sorted(clients["Name"].dropna().unique().tolist()) or ["—"]
        jclient=b.selectbox("Client",names)
        a2,b2,c2=st.columns(3)
        jcleaner=a2.selectbox("Cleaner",CLEANERS,index=2); jamount=b2.number_input("Amount ($)",min_value=0,step=5); jpaid=c2.selectbox("Paid?",["Yes","No"])
        if st.form_submit_button("➕ Log job"):
            ctype=""
            row=clients[clients["Name"]==jclient]
            if not row.empty: ctype=row.iloc[0]["Type"]
            new=pd.DataFrame([[jdate.isoformat(),jclient,ctype,jcleaner,jamount,jpaid]],columns=SERVICE_COLS)
            st.session_state.services=pd.concat([st.session_state.services,new],ignore_index=True)
            persist(); st.success("Job logged."); st.rerun()

    st.markdown("<div class='sec-h'>All jobs</div>", unsafe_allow_html=True)
    sl=services.sort_values("Date",ascending=False)
    rows="".join(f"<tr><td>{esc(r['Date'])}</td><td><b>{esc(r['Client'])}</b></td><td>{esc(r['Cleaner'])}</td>"
                 f"<td><span class='pill {'Yes' if str(r['Paid'])=='Yes' else 'No'}'>{esc(r['Paid'])}</span></td>"
                 f"<td class='r'><b>{money(to_num(r['Amount']))}</b></td>"
                 f"<td class='r' style='color:var(--muted)'>{money(to_num(r['Amount'])*0.2)}</td></tr>" for _,r in sl.iterrows())
    st.markdown(f"<div class='card'><table class='t'><tr><th>Date</th><th>Client</th><th>Cleaner</th><th>Paid</th><th class='r'>Amount</th><th class='r'>Your cut</th></tr>{rows}</table></div>", unsafe_allow_html=True)

    if len(services):
        with st.expander("🗑  Remove a job"):
            slabels=[f"{r['Date']} — {r['Client']} ({money(to_num(r['Amount']))})" for _,r in services.iterrows()]
            pj=st.selectbox("Choose job",range(len(slabels)),format_func=lambda i:slabels[i])
            if st.button("Remove this job"):
                st.session_state.services=st.session_state.services.drop(st.session_state.services.index[pj]).reset_index(drop=True)
                persist(); st.success("Removed."); st.rerun()
