import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
from datetime import datetime, timedelta
import time
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="My Portfolio Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── PASSWORD PROTECTION ───────────────────────────────────────────────────────
PASSWORD = "Sagar@123"  # Change this to your password

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
        <div style='text-align:center; padding: 80px 0 30px 0;'>
            <h1 style='font-size:3rem;'>📊 My Portfolio</h1>
            <p style='color:#888; font-size:1.1rem;'>Personal Investment Dashboard</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pwd = st.text_input("🔐 Password डालें", type="password", placeholder="Enter your password")
            if st.button("Login →", use_container_width=True, type="primary"):
                if pwd == PASSWORD:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ गलत password! फिर से try करें।")
        return False
    return True

# ─── GOOGLE SHEET DATA ────────────────────────────────────────────────────────
SHEET_ID = "1NslHsXqKu1nNW-9mqu_v6lw40PPpPBI1woR4s-E9Wc0"

def get_sheet_csv(gid):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"
    try:
        df = pd.read_csv(url, header=None)
        return df
    except:
        return None

# ─── STATIC DATA (fallback & initial load) ───────────────────────────────────
def get_listed_shares_data():
    data = [
        {"name": "Adani Gas",              "ticker": "ATGL.NS",        "qty": 40,   "buy_rate": 737.96},
        {"name": "Adani Power",            "ticker": "ADANIPOWER.NS",  "qty": 1,    "buy_rate": 147.62},
        {"name": "Akshar Spintex",         "ticker": "AKSHAR.NS",      "qty": 151,  "buy_rate": 0.66},
        {"name": "AvenuesAI (CCAvenue)",   "ticker": "CCAVENUE.NS",    "qty": 5000, "buy_rate": 15.67},
        {"name": "GAIL",                   "ticker": "GAIL.NS",        "qty": 50,   "buy_rate": 152.36},
        {"name": "GTL Infra",              "ticker": "GTLINFRA.NS",    "qty": 10100,"buy_rate": 1.27},
        {"name": "IRB Infra",              "ticker": "IRB.NS",         "qty": 5000, "buy_rate": 27.4},
        {"name": "IRFC",                   "ticker": "IRFC.NS",        "qty": 730,  "buy_rate": 136.21},
        {"name": "ITC",                    "ticker": "ITC.NS",         "qty": 50,   "buy_rate": 307.58},
        {"name": "JIO Financial",          "ticker": "JIOFIN.NS",      "qty": 100,  "buy_rate": 243.89},
        {"name": "Mishtann Foods",         "ticker": "MISHTANN.BO",    "qty": 150,  "buy_rate": 3.69},
        {"name": "NTPC Green Energy",      "ticker": "NTPCGREEN.NS",   "qty": 271,  "buy_rate": 94.72},
        {"name": "Orient Green Power",     "ticker": "ORIENTGREEN.BO", "qty": 8020, "buy_rate": 13.6},
        {"name": "Suzlon",                 "ticker": "SUZLON.NS",      "qty": 475,  "buy_rate": 53.39},
        {"name": "Tata Motors CV",         "ticker": "TATAMOTORS.NS",  "qty": 10,   "buy_rate": 319.72},
        {"name": "Tata Motors PV",         "ticker": "TATAMOTORS.NS",  "qty": 20,   "buy_rate": 519.98},
        {"name": "Tata Technologies",      "ticker": "TATATECH.NS",    "qty": 150,  "buy_rate": 884.09},
        {"name": "Tatia Global Venture",   "ticker": "TATIAGLOB.BO",   "qty": 170,  "buy_rate": 2.97},
        {"name": "Vidya Wires",            "ticker": "VIDYAWIRES.BO",  "qty": 200,  "buy_rate": 49.67},
        {"name": "Vodafone Idea",          "ticker": "IDEA.NS",        "qty": 100,  "buy_rate": 7.81},
        {"name": "Wipro",                  "ticker": "WIPRO.NS",       "qty": 200,  "buy_rate": 197.48},
        {"name": "Xchanging Solutions",    "ticker": "XCHANGING.NS",   "qty": 2500, "buy_rate": 106.22},
        {"name": "Yes Bank",               "ticker": "YESBANK.NS",     "qty": 1,    "buy_rate": 22.32},
    ]
    return pd.DataFrame(data)

def get_unlisted_shares_data():
    data = [
        {"name": "NSE (National Stock Exchange)", "qty": 41,   "buy_rate": 2027.92, "current_rate": 1955},
        {"name": "MSE (Metropolitan SE)",         "qty": 4000, "buy_rate": 5.3,     "current_rate": 7.0},
    ]
    return pd.DataFrame(data)

def get_mutual_fund_data():
    data = [
        {"name": "ICICI Pru Large & Mid Cap",      "amfi": 120596, "units": 134.131,  "invested": 46000,    "nav": 1151.83},
        {"name": "Bandhan Small Cap Fund",          "amfi": 147946, "units": 741.531,  "invested": 30000,    "nav": 51.335},
        {"name": "Motilal Oswal Digital India",     "amfi": 152964, "units": 1145.416, "invested": 26000,    "nav": 8.9923},
        {"name": "Nippon India Power & Infra",      "amfi": 118763, "units": 86.84,    "invested": 25000,    "nav": 403.0918},
        {"name": "ICICI Pru Multi Asset Fund",      "amfi": 120334, "units": 338.455,  "invested": 22000,    "nav": 898.8148},
        {"name": "JioBlackRock Nifty 50 Index",     "amfi": 153787, "units": 1548.025, "invested": 19000,    "nav": 9.8061},
        {"name": "Motilal Oswal Midcap Fund",       "amfi": 147622, "units": 165.234,  "invested": 17500,    "nav": 39.9191},
        {"name": "Tata BSE Select Business Groups", "amfi": 153132, "units": 1007.411, "invested": 16000,    "nav": 10.2289},
        {"name": "Axis ELSS Tax Saver Fund",        "amfi": 120503, "units": 185.748,  "invested": 12154.98, "nav": 105.9826},
        {"name": "Axis Momentum Fund",              "amfi": 153083, "units": 804.888,  "invested": 11000,    "nav": 9.26},
        {"name": "SBI Contra Direct Plan",          "amfi": 119835, "units": 23.951,   "invested": 9000,     "nav": 411.7989},
        {"name": "JioBlackRock Flexi Cap Fund",     "amfi": 153859, "units": 536.547,  "invested": 6000,     "nav": 9.84},
        {"name": "JioBlackRock Sector Rotation",    "amfi": 154082, "units": 557.22,   "invested": 6000,     "nav": 9.7351},
    ]
    return pd.DataFrame(data)

def get_loan_data():
    data = [
        {"month": "April 2026",     "navi": 28850, "piramal": 20796, "total": 49646, "status": "Clear"},
        {"month": "May 2026",       "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "June 2026",      "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "July 2026",      "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "August 2026",    "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "September 2026", "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "October 2026",   "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "November 2026",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "December 2026",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "January 2027",   "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "February 2027",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "March 2027",     "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "April 2027",     "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "May 2027",       "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "June 2027",      "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "July 2027",      "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "August 2027",    "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "September 2027", "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "October 2027",   "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "November 2027",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "December 2027",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "January 2028",   "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "February 2028",  "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "March 2028",     "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "April 2028",     "navi": 28850, "piramal": 20796, "total": 49646, "status": "Hold"},
        {"month": "May 2028",       "navi": 28850, "piramal": 18872, "total": 47722, "status": "Hold"},
        {"month": "June 2028",      "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "July 2028",      "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "August 2028",    "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "September 2028", "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "October 2028",   "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "November 2028",  "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "December 2028",  "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "January 2029",   "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "February 2029",  "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "March 2029",     "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "April 2029",     "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "May 2029",       "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "June 2029",      "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "July 2029",      "navi": 28850, "piramal": 0,     "total": 28850, "status": "Hold"},
        {"month": "August 2029",    "navi": 17484, "piramal": 0,     "total": 17484, "status": "Hold"},
    ]
    return pd.DataFrame(data)

# ─── LIVE PRICE FETCHER ───────────────────────────────────────────────────────
@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_live_prices(tickers):
    prices = {}
    unique_tickers = list(set(tickers))
    for ticker in unique_tickers:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="1d")
            if not hist.empty:
                prices[ticker] = round(hist["Close"].iloc[-1], 2)
            else:
                prices[ticker] = None
        except:
            prices[ticker] = None
    return prices

@st.cache_data(ttl=3600)  # Cache NAV for 1 hour
def fetch_mf_nav(amfi_codes):
    navs = {}
    try:
        url = "https://www.amfiindia.com/spages/NAVAll.txt"
        response = requests.get(url, timeout=10)
        lines = response.text.split("\n")
        for line in lines:
            parts = line.split(";")
            if len(parts) >= 5:
                try:
                    code = int(parts[0].strip())
                    nav = float(parts[4].strip())
                    if code in amfi_codes:
                        navs[code] = nav
                except:
                    pass
    except:
        pass
    return navs

# ─── FORMATTING ───────────────────────────────────────────────────────────────
def fmt_inr(val):
    try:
        val = float(val)
        if abs(val) >= 1e7:
            return f"₹{val/1e7:.2f} Cr"
        elif abs(val) >= 1e5:
            return f"₹{val/1e5:.2f} L"
        else:
            return f"₹{val:,.0f}"
    except:
        return "₹0"

def color_val(val):
    try:
        v = float(val)
        if v > 0:
            return f"🟢 ₹{v:,.2f}"
        elif v < 0:
            return f"🔴 ₹{v:,.2f}"
        return f"⚪ ₹{v:,.2f}"
    except:
        return str(val)

def color_pct(val):
    try:
        v = float(val)
        if v > 0:
            return f"🟢 +{v:.2f}%"
        elif v < 0:
            return f"🔴 {v:.2f}%"
        return f"⚪ {v:.2f}%"
    except:
        return str(val)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main { background: #0f0f1a; }

    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #2d2d4e;
        border-radius: 16px;
        padding: 20px 24px;
        margin: 6px 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .metric-card h3 { color: #8888aa; font-size: 0.8rem; font-weight: 500; margin: 0 0 8px 0; text-transform: uppercase; letter-spacing: 1px; }
    .metric-card .value { color: #fff; font-size: 1.5rem; font-weight: 700; margin: 0; }
    .metric-card .sub { color: #6677aa; font-size: 0.8rem; margin-top: 4px; }

    .profit { color: #00d4aa !important; }
    .loss   { color: #ff4d6d !important; }
    .neutral{ color: #aaaacc !important; }

    .gateway-card {
        background: linear-gradient(135deg, #0d1117 0%, #1a1a2e 100%);
        border-radius: 20px;
        padding: 30px;
        border: 1px solid #2d2d4e;
        text-align: center;
        margin: 10px 0;
    }

    .section-header {
        color: #e0e0ff;
        font-size: 1.4rem;
        font-weight: 700;
        padding: 15px 0 5px 0;
        border-bottom: 2px solid #2d2d4e;
        margin-bottom: 20px;
    }

    .stDataFrame { border-radius: 12px; overflow: hidden; }
    .stDataFrame thead { background: #1a1a2e !important; }

    .sidebar-info {
        background: #1a1a2e;
        border-radius: 10px;
        padding: 12px;
        margin: 8px 0;
        border: 1px solid #2d2d4e;
        font-size: 0.85rem;
    }

    .tag-green { background: #003322; color: #00d4aa; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
    .tag-red   { background: #330011; color: #ff4d6d; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

    .stButton button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetric"] {
        background: #1a1a2e;
        border: 1px solid #2d2d4e;
        border-radius: 12px;
        padding: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# ─── MAIN APP ─────────────────────────────────────────────────────────────────
def main():
    inject_css()

    if not check_password():
        return

    # ── SIDEBAR ──
    with st.sidebar:
        st.markdown("### 📊 My Portfolio")
        st.markdown(f"<small>Last Updated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}</small>", unsafe_allow_html=True)
        st.divider()

        page = st.radio("📌 Section", [
            "🏠 Main Gateway",
            "📈 Listed Shares",
            "🏢 Unlisted Shares",
            "💼 Mutual Funds",
            "🏦 Loan Details"
        ])

        st.divider()
        if st.button("🔄 Refresh Live Prices"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("""
        <div class='sidebar-info'>
        ⏱️ Prices auto-refresh every <b>5 min</b><br>
        📊 NAV updates every <b>1 hour</b>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    # ── LOAD DATA ──
    df_listed   = get_listed_shares_data()
    df_unlisted = get_unlisted_shares_data()
    df_mf       = get_mutual_fund_data()
    df_loan     = get_loan_data()

    # ── FETCH LIVE PRICES ──
    with st.spinner("📡 Live prices fetch हो रही हैं..."):
        tickers = df_listed["ticker"].tolist()
        live_prices = fetch_live_prices(tickers)

        # Apply live prices
        df_listed["current_price"] = df_listed["ticker"].map(
            lambda t: live_prices.get(t) if live_prices.get(t) else None
        )

        # Tata Motors special case (both CV and PV same ticker)
        tata_price = live_prices.get("TATAMOTORS.NS")
        df_listed.loc[df_listed["ticker"] == "TATAMOTORS.NS", "current_price"] = tata_price

        df_listed["current_price"] = pd.to_numeric(df_listed["current_price"], errors="coerce")
        df_listed["invested"]      = df_listed["qty"] * df_listed["buy_rate"]
        df_listed["current_value"] = df_listed["qty"] * df_listed["current_price"]
        df_listed["pnl"]           = df_listed["current_value"] - df_listed["invested"]
        df_listed["pnl_pct"]       = (df_listed["pnl"] / df_listed["invested"] * 100).round(2)

    # ── FETCH LIVE MF NAV ──
    with st.spinner("📡 Mutual Fund NAV fetch हो रही है..."):
        amfi_codes = df_mf["amfi"].tolist()
        live_navs  = fetch_mf_nav(amfi_codes)
        df_mf["live_nav"]       = df_mf["amfi"].map(lambda c: live_navs.get(c, None))
        df_mf["nav_used"]       = df_mf["live_nav"].fillna(df_mf["nav"])
        df_mf["current_value"]  = df_mf["units"] * df_mf["nav_used"]
        df_mf["pnl"]            = df_mf["current_value"] - df_mf["invested"]
        df_mf["pnl_pct"]        = (df_mf["pnl"] / df_mf["invested"] * 100).round(2)

    # ── UNLISTED SHARES ──
    df_unlisted["invested"]      = df_unlisted["qty"] * df_unlisted["buy_rate"]
    df_unlisted["current_value"] = df_unlisted["qty"] * df_unlisted["current_rate"]
    df_unlisted["pnl"]           = df_unlisted["current_value"] - df_unlisted["invested"]
    df_unlisted["pnl_pct"]       = (df_unlisted["pnl"] / df_unlisted["invested"] * 100).round(2)

    # ── SUMMARY TOTALS ──
    total_listed_invested     = df_listed["invested"].sum()
    total_listed_current      = df_listed["current_value"].sum()
    total_listed_pnl          = df_listed["pnl"].sum()

    total_unlisted_invested   = df_unlisted["invested"].sum()
    total_unlisted_current    = df_unlisted["current_value"].sum()
    total_unlisted_pnl        = df_unlisted["pnl"].sum()

    total_mf_invested         = df_mf["invested"].sum()
    total_mf_current          = df_mf["current_value"].sum()
    total_mf_pnl              = df_mf["pnl"].sum()

    total_assets = total_listed_current + total_unlisted_current + total_mf_current

    # LOAN - remaining EMIs (Hold status only)
    df_loan_pending           = df_loan[df_loan["status"] == "Hold"]
    total_navi_remaining      = df_loan_pending["navi"].sum()
    total_piramal_remaining   = df_loan_pending["piramal"].sum()
    total_loan_remaining      = df_loan_pending["total"].sum()
    total_loan_all            = df_loan["total"].sum()

    net_worth = total_assets - total_loan_remaining

    # ══════════════════════════════════════════════════════════════════
    # PAGE: MAIN GATEWAY
    # ══════════════════════════════════════════════════════════════════
    if page == "🏠 Main Gateway":
        st.markdown("<h1 style='color:#e0e0ff;'>🏠 Portfolio Gateway</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#666;'>As on {datetime.now().strftime('%d %B %Y')}</p>", unsafe_allow_html=True)

        # NET WORTH BANNER
        nw_color = "#00d4aa" if net_worth >= 0 else "#ff4d6d"
        st.markdown(f"""
        <div class='gateway-card'>
            <p style='color:#888; font-size:0.9rem; margin:0;'>💎 TOTAL NET WORTH</p>
            <h1 style='color:{nw_color}; font-size:3rem; margin:10px 0;'>{fmt_inr(net_worth)}</h1>
            <p style='color:#555; font-size:0.85rem;'>Assets − Liabilities (Pending Loans)</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # ── ASSETS ──
        st.markdown("<div class='section-header'>💰 ASSETS</div>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            pnl_color = "profit" if total_listed_pnl >= 0 else "loss"
            st.markdown(f"""
            <div class='metric-card'>
                <h3>📈 Listed Shares</h3>
                <div class='value'>{fmt_inr(total_listed_current)}</div>
                <div class='sub'>Invested: {fmt_inr(total_listed_invested)}</div>
                <div class='sub {pnl_color}'>P&L: {fmt_inr(total_listed_pnl)} ({total_listed_pnl/total_listed_invested*100:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            pnl_color2 = "profit" if total_unlisted_pnl >= 0 else "loss"
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏢 Unlisted Shares</h3>
                <div class='value'>{fmt_inr(total_unlisted_current)}</div>
                <div class='sub'>Invested: {fmt_inr(total_unlisted_invested)}</div>
                <div class='sub {pnl_color2}'>P&L: {fmt_inr(total_unlisted_pnl)} ({total_unlisted_pnl/total_unlisted_invested*100:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with c3:
            pnl_color3 = "profit" if total_mf_pnl >= 0 else "loss"
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💼 Mutual Funds</h3>
                <div class='value'>{fmt_inr(total_mf_current)}</div>
                <div class='sub'>Invested: {fmt_inr(total_mf_invested)}</div>
                <div class='sub {pnl_color3}'>P&L: {fmt_inr(total_mf_pnl)} ({total_mf_pnl/total_mf_invested*100:.1f}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏆 Total Assets</h3>
                <div class='value profit'>{fmt_inr(total_assets)}</div>
                <div class='sub'>Total Invested: {fmt_inr(total_listed_invested+total_unlisted_invested+total_mf_invested)}</div>
                <div class='sub'>3 categories combined</div>
            </div>
            """, unsafe_allow_html=True)

        # ── LIABILITIES ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>🏦 LIABILITIES</div>", unsafe_allow_html=True)
        c5, c6, c7 = st.columns(3)

        with c5:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏠 Navi Loan (Remaining)</h3>
                <div class='value loss'>{fmt_inr(total_navi_remaining)}</div>
                <div class='sub'>EMI: ₹28,850/month</div>
                <div class='sub'>{len(df_loan_pending)} EMIs pending</div>
            </div>
            """, unsafe_allow_html=True)

        with c6:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>🏦 Piramal Loan (Remaining)</h3>
                <div class='value loss'>{fmt_inr(total_piramal_remaining)}</div>
                <div class='sub'>EMI: ₹20,796/month (varies)</div>
                <div class='sub'>Ends May 2028</div>
            </div>
            """, unsafe_allow_html=True)

        with c7:
            st.markdown(f"""
            <div class='metric-card'>
                <h3>💸 Total Liability</h3>
                <div class='value loss'>{fmt_inr(total_loan_remaining)}</div>
                <div class='sub'>Combined pending EMIs</div>
                <div class='sub'>Total EMI: ₹{df_loan_pending['total'].mean():,.0f}/month avg</div>
            </div>
            """, unsafe_allow_html=True)

        # ── CHARTS ──
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'>📊 Portfolio Breakdown</div>", unsafe_allow_html=True)

        col_pie, col_bar = st.columns(2)

        with col_pie:
            labels = ["Listed Shares", "Unlisted Shares", "Mutual Funds"]
            values = [total_listed_current, total_unlisted_current, total_mf_current]
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.5,
                marker_colors=["#4f46e5", "#7c3aed", "#00d4aa"]
            )])
            fig_pie.update_layout(
                title="Asset Allocation",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccccee",
                showlegend=True,
                height=350
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            categories  = ["Listed\nShares", "Unlisted\nShares", "Mutual\nFunds"]
            invested_v  = [total_listed_invested, total_unlisted_invested, total_mf_invested]
            current_v   = [total_listed_current,  total_unlisted_current,  total_mf_current]

            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Invested", x=categories, y=invested_v, marker_color="#4f46e5"))
            fig_bar.add_trace(go.Bar(name="Current",  x=categories, y=current_v,  marker_color="#00d4aa"))
            fig_bar.update_layout(
                title="Invested vs Current Value",
                barmode="group",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font_color="#ccccee",
                height=350
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # Assets vs Liabilities bar
        fig_anl = go.Figure()
        fig_anl.add_trace(go.Bar(x=["Total Assets"], y=[total_assets],         name="Assets",      marker_color="#00d4aa"))
        fig_anl.add_trace(go.Bar(x=["Total Loans"],  y=[total_loan_remaining], name="Liabilities", marker_color="#ff4d6d"))
        fig_anl.add_trace(go.Bar(x=["Net Worth"],    y=[max(net_worth, 0)],    name="Net Worth",   marker_color="#4f46e5"))
        fig_anl.update_layout(
            title="Assets vs Liabilities vs Net Worth",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccee",
            height=300,
            showlegend=True
        )
        st.plotly_chart(fig_anl, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # PAGE: LISTED SHARES
    # ══════════════════════════════════════════════════════════════════
    elif page == "📈 Listed Shares":
        st.markdown("<h1 style='color:#e0e0ff;'>📈 Listed Shares Portfolio</h1>", unsafe_allow_html=True)

        # Summary metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Invested",    fmt_inr(total_listed_invested))
        c2.metric("📊 Current Value",     fmt_inr(total_listed_current))
        c3.metric("📈 Total P&L",         fmt_inr(total_listed_pnl),
                  f"{total_listed_pnl/total_listed_invested*100:.2f}%")
        c4.metric("🔢 Stocks",            str(len(df_listed)))

        st.markdown("---")

        # Table
        display_df = df_listed.copy()
        display_df["Invested (₹)"]      = display_df["invested"].apply(lambda x: f"₹{x:,.0f}")
        display_df["Current Price"]     = display_df["current_price"].apply(lambda x: f"₹{x:,.2f}" if pd.notna(x) else "N/A")
        display_df["Current Value (₹)"] = display_df["current_value"].apply(lambda x: f"₹{x:,.0f}" if pd.notna(x) else "N/A")
        display_df["P&L (₹)"]           = display_df["pnl"].apply(lambda x: f"{'+'if x>=0 else ''}₹{x:,.0f}" if pd.notna(x) else "N/A")
        display_df["P&L (%)"]           = display_df["pnl_pct"].apply(lambda x: f"{'+'if x>=0 else ''}{x:.2f}%" if pd.notna(x) else "N/A")

        show_cols = {
            "name":           "Stock Name",
            "ticker":         "NSE/BSE Symbol",
            "qty":            "Qty",
            "buy_rate":       "Buy Rate",
            "Invested (₹)":   "Invested",
            "Current Price":  "Live Price",
            "Current Value (₹)": "Current Value",
            "P&L (₹)":        "P&L Amount",
            "P&L (%)":        "P&L %",
        }
        display_df = display_df[list(show_cols.keys())].rename(columns=show_cols)

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Top gainers / losers
        df_valid = df_listed.dropna(subset=["pnl_pct"])
        st.markdown("<br>", unsafe_allow_html=True)
        col_g, col_l = st.columns(2)

        with col_g:
            st.markdown("#### 🟢 Top Gainers")
            gainers = df_valid.nlargest(5, "pnl_pct")[["name", "pnl_pct", "pnl"]]
            for _, row in gainers.iterrows():
                st.markdown(f"**{row['name']}** &nbsp; <span class='tag-green'>+{row['pnl_pct']:.2f}%</span> &nbsp; ₹{row['pnl']:,.0f}", unsafe_allow_html=True)

        with col_l:
            st.markdown("#### 🔴 Top Losers")
            losers = df_valid.nsmallest(5, "pnl_pct")[["name", "pnl_pct", "pnl"]]
            for _, row in losers.iterrows():
                st.markdown(f"**{row['name']}** &nbsp; <span class='tag-red'>{row['pnl_pct']:.2f}%</span> &nbsp; ₹{row['pnl']:,.0f}", unsafe_allow_html=True)

        # Chart
        fig = px.bar(
            df_valid.sort_values("pnl"),
            x="name", y="pnl",
            color="pnl",
            color_continuous_scale=["#ff4d6d", "#ffffff", "#00d4aa"],
            title="Stock-wise P&L",
            labels={"pnl": "P&L (₹)", "name": "Stock"}
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccee",
            xaxis_tickangle=-45,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # PAGE: UNLISTED SHARES
    # ══════════════════════════════════════════════════════════════════
    elif page == "🏢 Unlisted Shares":
        st.markdown("<h1 style='color:#e0e0ff;'>🏢 Unlisted Shares Portfolio</h1>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("💰 Total Invested",  fmt_inr(total_unlisted_invested))
        c2.metric("📊 Current Value",   fmt_inr(total_unlisted_current))
        c3.metric("📈 Total P&L",       fmt_inr(total_unlisted_pnl),
                  f"{total_unlisted_pnl/total_unlisted_invested*100:.2f}%")

        st.markdown("---")
        st.info("⚠️ Unlisted shares का price manually updated है (real-time price available नहीं होती)")

        display_ul = df_unlisted.copy()
        display_ul["Invested (₹)"]      = display_ul["invested"].apply(lambda x: f"₹{x:,.2f}")
        display_ul["Current Value (₹)"] = display_ul["current_value"].apply(lambda x: f"₹{x:,.2f}")
        display_ul["P&L (₹)"]           = display_ul["pnl"].apply(lambda x: f"{'+'if x>=0 else ''}₹{x:,.2f}")
        display_ul["P&L (%)"]           = display_ul["pnl_pct"].apply(lambda x: f"{'+'if x>=0 else ''}{x:.2f}%")

        show_ul = {
            "name":              "Company Name",
            "qty":               "Quantity",
            "buy_rate":          "Buy Rate (₹)",
            "current_rate":      "Current Rate (₹)",
            "Invested (₹)":      "Invested",
            "Current Value (₹)": "Current Value",
            "P&L (₹)":           "P&L Amount",
            "P&L (%)":           "P&L %",
        }
        st.dataframe(display_ul[list(show_ul.keys())].rename(columns=show_ul),
                     use_container_width=True, hide_index=True)

        # Pie
        fig_u = go.Figure(data=[go.Pie(
            labels=df_unlisted["name"],
            values=df_unlisted["current_value"],
            hole=0.4,
            marker_colors=["#4f46e5", "#00d4aa"]
        )])
        fig_u.update_layout(
            title="Unlisted Shares Allocation",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccee",
            height=350
        )
        st.plotly_chart(fig_u, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # PAGE: MUTUAL FUNDS
    # ══════════════════════════════════════════════════════════════════
    elif page == "💼 Mutual Funds":
        st.markdown("<h1 style='color:#e0e0ff;'>💼 Mutual Fund Portfolio</h1>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💰 Total Invested",  fmt_inr(total_mf_invested))
        c2.metric("📊 Current Value",   fmt_inr(total_mf_current))
        c3.metric("📈 Total P&L",       fmt_inr(total_mf_pnl),
                  f"{total_mf_pnl/total_mf_invested*100:.2f}%")
        c4.metric("🔢 Funds",           str(len(df_mf)))

        st.markdown("---")

        display_mf = df_mf.copy()
        nav_src = display_mf.apply(
            lambda r: f"₹{r['live_nav']:.4f} 🟢 Live" if pd.notna(r['live_nav']) else f"₹{r['nav']:.4f} 🔵 Cached",
            axis=1
        )
        display_mf["NAV"]            = nav_src
        display_mf["Invested"]       = display_mf["invested"].apply(lambda x: f"₹{x:,.2f}")
        display_mf["Current Value"]  = display_mf["current_value"].apply(lambda x: f"₹{x:,.2f}")
        display_mf["P&L"]            = display_mf["pnl"].apply(lambda x: f"{'+'if x>=0 else ''}₹{x:,.2f}")
        display_mf["P&L %"]          = display_mf["pnl_pct"].apply(lambda x: f"{'+'if x>=0 else ''}{x:.2f}%")

        show_mf = {
            "name":          "Scheme Name",
            "amfi":          "AMFI Code",
            "units":         "Units",
            "Invested":      "Invested",
            "NAV":           "NAV (Live)",
            "Current Value": "Current Value",
            "P&L":           "P&L Amount",
            "P&L %":         "P&L %",
        }
        st.dataframe(display_mf[list(show_mf.keys())].rename(columns=show_mf),
                     use_container_width=True, hide_index=True)

        # Fund P&L chart
        fig_mf = px.bar(
            df_mf.sort_values("pnl"),
            x="name", y="pnl",
            color="pnl",
            color_continuous_scale=["#ff4d6d", "#ffffff", "#00d4aa"],
            title="Fund-wise P&L",
            labels={"pnl": "P&L (₹)", "name": "Fund"}
        )
        fig_mf.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccee",
            xaxis_tickangle=-30,
            height=420
        )
        st.plotly_chart(fig_mf, use_container_width=True)

    # ══════════════════════════════════════════════════════════════════
    # PAGE: LOAN DETAILS
    # ══════════════════════════════════════════════════════════════════
    elif page == "🏦 Loan Details":
        st.markdown("<h1 style='color:#e0e0ff;'>🏦 Loan EMI Schedule</h1>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🏠 Navi Pending",    fmt_inr(total_navi_remaining))
        c2.metric("🏦 Piramal Pending", fmt_inr(total_piramal_remaining))
        c3.metric("💸 Total Pending",   fmt_inr(total_loan_remaining))
        c4.metric("✅ EMIs Cleared",    str(len(df_loan[df_loan["status"]=="Clear"])))

        st.markdown("---")

        # Color rows
        def style_status(val):
            if val == "Clear":
                return "background-color: #003322; color: #00d4aa"
            else:
                return "background-color: #330011; color: #ff4d6d"

        styled = df_loan.rename(columns={
            "month": "Month", "navi": "Navi EMI (₹)",
            "piramal": "Piramal EMI (₹)", "total": "Total EMI (₹)", "status": "Status"
        }).style.applymap(style_status, subset=["Status"])

        st.dataframe(styled, use_container_width=True, hide_index=True)

        # EMI timeline chart
        df_chart = df_loan.copy()
        df_chart["Month_idx"] = range(len(df_chart))
        fig_loan = go.Figure()
        fig_loan.add_trace(go.Bar(name="Navi",    x=df_chart["month"], y=df_chart["navi"],    marker_color="#4f46e5"))
        fig_loan.add_trace(go.Bar(name="Piramal", x=df_chart["month"], y=df_chart["piramal"], marker_color="#7c3aed"))
        fig_loan.update_layout(
            title="Monthly EMI Schedule",
            barmode="stack",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ccccee",
            xaxis_tickangle=-45,
            height=420,
            xaxis_title="Month",
            yaxis_title="EMI Amount (₹)"
        )
        st.plotly_chart(fig_loan, use_container_width=True)

        # Summary
        st.markdown(f"""
        <div class='metric-card' style='margin-top:20px;'>
            <h3>📋 Loan Summary</h3>
            <p style='color:#ccc;'>🏠 <b>Navi Loan:</b> ₹28,850/month → August 2029 तक</p>
            <p style='color:#ccc;'>🏦 <b>Piramal Loan:</b> ₹20,796/month → May 2028 तक, फिर बंद</p>
            <p style='color:#ccc;'>💸 <b>Total EMI (अभी):</b> ₹49,646/month</p>
            <p style='color:#ccc;'>✅ <b>April 2026:</b> Already Clear</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
