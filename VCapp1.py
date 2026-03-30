import os
os.environ["ANTHROPIC_API_KEY"] = "YOUR_API_KEY_HERE"

import streamlit as st
import anthropic
import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import sqlite3
import base64
from datetime import datetime, date
import io

# ── LOGO HELPER ────────────────────────────────────────────────────────────────
def get_logo_b64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

LOGO_B64 = get_logo_b64()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AlphaLens | VC & PE Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── DATABASE SETUP ─────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("alphalens.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS deal_flow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, sector TEXT, stage TEXT,
            valuation REAL, round_size REAL, lead_investor TEXT,
            score INTEGER, status TEXT, notes TEXT,
            date_added TEXT, website TEXT, hq TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, sector TEXT, investment_date TEXT,
            invested_amount REAL, current_valuation REAL,
            ownership_pct REAL, revenue REAL, revenue_growth REAL,
            burn_rate REAL, runway_months REAL, arr REAL,
            employees INTEGER, stage TEXT, notes TEXT,
            last_updated TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS pitch_decks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT, date_analyzed TEXT,
            overall_score INTEGER, market_score INTEGER,
            team_score INTEGER, product_score INTEGER,
            financial_score INTEGER, risk_score INTEGER,
            full_analysis TEXT, investment_verdict TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

  :root {
    --bg:      #0a0b0e; --bg2: #0f1015; --bg3: #151720;
    --border:  #1e2130; --border2: #2a2f45;
    --gold:    #c9a84c; --gold2: #e8c97a;
    --teal:    #3ecfb2; --red: #e05c5c;
    --muted:   #4a5075; --text: #d4d8f0;
    --text2:   #8890b8; --white: #f0f2ff;
    --purple:  #a78bfa; --blue: #60a5fa;
  }
  html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; background-color: var(--bg) !important; color: var(--text); }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 1.5rem 2.5rem 3rem !important; max-width: 100% !important; }

  .alphalens-header { display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid var(--border2); padding-bottom:1.2rem; margin-bottom:2rem; }
  .alphalens-logo { font-family:'Playfair Display',serif; font-size:1.9rem; font-weight:700; color:var(--white); letter-spacing:-0.5px; }
  .alphalens-logo span { color:var(--gold); }
  .alphalens-tagline { font-family:'IBM Plex Mono',monospace; font-size:0.68rem; color:var(--muted); letter-spacing:2px; text-transform:uppercase; }
  .header-badge { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:var(--teal); border:1px solid var(--teal); border-radius:2px; padding:2px 8px; letter-spacing:1.5px; }

  .stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:1px solid var(--border2) !important; gap:0 !important; }
  .stTabs [data-baseweb="tab"] { font-family:'IBM Plex Mono',monospace !important; font-size:0.70rem !important; letter-spacing:1.5px !important; text-transform:uppercase !important; color:var(--muted) !important; background:transparent !important; border:none !important; border-bottom:2px solid transparent !important; padding:0.6rem 1.2rem !important; }
  .stTabs [aria-selected="true"] { color:var(--gold) !important; border-bottom:2px solid var(--gold) !important; }
  .stTabs [data-baseweb="tab-panel"] { padding-top:1.5rem !important; }

  .card { background:var(--bg3); border:1px solid var(--border); border-radius:4px; padding:1.4rem 1.6rem; margin-bottom:1rem; }
  .section-label { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; letter-spacing:2.5px; text-transform:uppercase; color:var(--gold); border-left:2px solid var(--gold); padding-left:0.7rem; margin:1.6rem 0 0.8rem; }
  .metric-pill { background:var(--bg3); border:1px solid var(--border); border-radius:4px; padding:0.8rem 1.2rem; min-width:140px; }
  .metric-pill .label { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; letter-spacing:1.5px; text-transform:uppercase; color:var(--muted); }
  .metric-pill .val { font-family:'IBM Plex Mono',monospace; font-size:1.1rem; font-weight:600; color:var(--white); margin-top:3px; }
  .positive { color:var(--teal) !important; }
  .negative { color:var(--red) !important; }
  .divider { border:none; border-top:1px solid var(--border); margin:1.5rem 0; }

  .score-bar-wrap { background:var(--border); border-radius:2px; height:6px; margin-top:5px; }
  .score-bar { height:6px; border-radius:2px; }

  .deal-row { background:var(--bg3); border:1px solid var(--border); border-radius:4px; padding:1rem 1.2rem; margin-bottom:0.6rem; display:flex; align-items:center; justify-content:space-between; }
  .deal-company { font-weight:600; color:var(--white); font-size:0.95rem; }
  .deal-meta { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); margin-top:3px; }

  .verdict-pass { background:rgba(62,207,178,0.1); border:1px solid var(--teal); border-radius:4px; padding:1rem 1.4rem; color:var(--teal); font-weight:600; }
  .verdict-pass-soft { background:rgba(201,168,76,0.1); border:1px solid var(--gold); border-radius:4px; padding:1rem 1.4rem; color:var(--gold); font-weight:600; }
  .verdict-fail { background:rgba(224,92,92,0.1); border:1px solid var(--red); border-radius:4px; padding:1rem 1.4rem; color:var(--red); font-weight:600; }

  .news-item { background:var(--bg3); border:1px solid var(--border); border-radius:4px; padding:1.2rem 1.4rem; margin-bottom:0.75rem; }
  .news-headline { font-size:0.92rem; font-weight:500; color:var(--white); margin-bottom:0.35rem; }
  .news-meta { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:var(--muted); }
  .news-summary { font-size:0.8rem; color:var(--text2); margin-top:0.5rem; line-height:1.6; }
  .news-tag { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:1px; text-transform:uppercase; border:1px solid; border-radius:2px; padding:1px 5px; margin-right:4px; }
  .tag-vc { color:var(--teal); border-color:var(--teal); }
  .tag-pe { color:var(--gold); border-color:var(--gold); }
  .tag-exit { color:var(--purple); border-color:var(--purple); }
  .tag-round { color:var(--blue); border-color:var(--blue); }

  .stTextInput > div > div > input, .stNumberInput > div > div > input,
  .stSelectbox > div > div, .stTextArea > div > div > textarea { background:var(--bg3) !important; border-color:var(--border2) !important; color:var(--text) !important; }
  .stTextInput label, .stNumberInput label, .stSelectbox label, .stSlider label, .stTextArea label { color:var(--text2) !important; font-size:0.8rem !important; }
  .stButton > button { background:var(--gold) !important; color:#0a0b0e !important; font-family:'IBM Plex Mono',monospace !important; font-size:0.72rem !important; letter-spacing:1.5px !important; text-transform:uppercase !important; font-weight:600 !important; border:none !important; border-radius:3px !important; padding:0.55rem 1.6rem !important; }
  .stButton > button:hover { background:var(--gold2) !important; }
  .stDataFrame { background:var(--bg3) !important; }
</style>
""", unsafe_allow_html=True)


# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="alphalens-header">
  <div style="display:flex; align-items:center; gap:1rem;">
    """ + (f'<img src="data:image/png;base64,{LOGO_B64}" style="width:65px;height:65px;object-fit:contain;filter:brightness(0) invert(1) sepia(1) saturate(2) hue-rotate(5deg) brightness(0.85);" />' if LOGO_B64 else """<svg width="60" height="60" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
      <defs><clipPath id="cc"><circle cx="100" cy="100" r="78"/></clipPath></defs>
      <circle cx="100" cy="100" r="87" fill="#0a0b0e" stroke="#c9a84c" stroke-width="2.5"/>
      <circle cx="100" cy="100" r="81" fill="#0a0b0e" stroke="#c9a84c" stroke-width="0.8" opacity="0.5"/>
      <g clip-path="url(#cc)">
        <ellipse cx="100" cy="100" rx="78" ry="14" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <ellipse cx="100" cy="100" rx="78" ry="34" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <ellipse cx="100" cy="100" rx="78" ry="58" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <line x1="22" y1="100" x2="178" y2="100" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <ellipse cx="100" cy="100" rx="16" ry="78" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <ellipse cx="100" cy="100" rx="40" ry="78" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <ellipse cx="100" cy="100" rx="63" ry="78" fill="none" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
        <line x1="100" y1="22" x2="100" y2="178" stroke="#c9a84c" stroke-width="0.6" opacity="0.35"/>
      </g>
      <path d="M62,130 Q42,120 38,100 Q34,76 46,58 Q40,42 50,34 Q58,38 62,48 Q66,36 76,30 Q80,42 82,50 Q90,36 104,34 Q104,48 100,56 Q114,44 126,48 Q120,60 116,68 Q130,62 136,74 Q124,86 120,92 Q134,86 138,98 Q126,112 118,116 Q128,126 124,138 Q112,130 106,128 Q108,142 100,148 Q92,138 86,136 Q80,148 72,150 Z" fill="#8a6a20" opacity="0.6"/>
      <path d="M74,148 Q58,138 54,118 Q50,96 58,78 Q66,58 84,52 Q100,48 114,60 Q128,72 126,96 Q124,120 110,136 Q96,150 82,150 Z" fill="#e8c97a"/>
      <path d="M80,80 Q86,74 94,76 Q98,82 92,86 Q82,88 80,84 Z" fill="#1a1000"/>
      <circle cx="87" cy="80" r="1.4" fill="white" opacity="0.9"/>
      <path d="M100,104 Q106,101 112,104 Q110,112 106,114 Q100,114 100,108 Z" fill="#8b4513"/>
      <path d="M96,114 Q106,120 116,114" stroke="#8b4513" stroke-width="1.2" fill="none"/>
      <line x1="46" y1="104" x2="96" y2="106" stroke="#e8d090" stroke-width="0.9" opacity="0.7"/>
      <line x1="44" y1="110" x2="96" y2="110" stroke="#e8d090" stroke-width="0.9" opacity="0.7"/>
      <line x1="116" y1="104" x2="148" y2="101" stroke="#e8d090" stroke-width="0.9" opacity="0.7"/>
      <line x1="116" y1="110" x2="148" y2="109" stroke="#e8d090" stroke-width="0.9" opacity="0.7"/>
      <path d="M110,52 Q118,40 128,38 Q124,52 118,58 Z" fill="#e8c97a"/>
    </svg>""") + """
    <div>
      <div class="alphalens-logo">Alpha<span>Lens</span></div>
      <div class="alphalens-tagline">VC · PE · Growth Intelligence Platform</div>
    </div>
  </div>
  <div class="header-badge">◈ LIVE INTELLIGENCE</div>
</div>
""", unsafe_allow_html=True)


# ── ANTHROPIC CLIENT ───────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return anthropic.Anthropic()

def stream_claude(prompt, system="", max_tokens=4000, use_search=False):
    client = get_client()
    kwargs = dict(
        model="claude-opus-4-5",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    if use_search:
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
    full = ""
    with client.messages.stream(**kwargs) as s:
        for t in s.text_stream:
            full += t
    return full

def analyze_pdf_with_claude(pdf_bytes, company_name):
    client = get_client()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    system = """You are a senior VC partner doing first-pass due diligence on a pitch deck.
    Analyze it like you would for an investment committee. Be direct, specific, and critical.
    Return ONLY valid JSON, no markdown, no preamble."""
    prompt = """Analyze this pitch deck and return a JSON object with exactly this structure:
    {
      "company_name": "...",
      "one_liner": "...",
      "sector": "...",
      "stage": "...",
      "scores": {
        "overall": 0-100,
        "market": 0-100,
        "team": 0-100,
        "product": 0-100,
        "financials": 0-100,
        "risk": 0-100
      },
      "market_size": {"tam": "...", "sam": "...", "som": "...", "assessment": "..."},
      "team_analysis": "...",
      "product_analysis": "...",
      "financial_analysis": "...",
      "key_risks": ["risk1", "risk2", "risk3", "risk4", "risk5"],
      "key_strengths": ["strength1", "strength2", "strength3"],
      "red_flags": ["flag1", "flag2"],
      "investment_verdict": "STRONG PASS | PASS | SOFT PASS | PASS WITH CONDITIONS | NO",
      "verdict_reasoning": "...",
      "suggested_valuation_range": "...",
      "next_steps": ["step1", "step2", "step3"]
    }"""
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=3000,
        system=system,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": prompt}
            ]
        }]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw)


def extract_deal_from_pdf(pdf_bytes):
    """Extract deal flow fields from any company PDF (pitch deck, one-pager, tearsheet)."""
    client = get_client()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system="Extract deal information from this document. Return ONLY valid JSON, no markdown.",
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": """Extract all available deal information and return this JSON structure (use null for missing fields):
{
  "company": "company name",
  "sector": "best matching sector from: AI/ML, Fintech, Healthcare, SaaS, Consumer, Deeptech, Crypto/Web3, Climate, Biotech, Other",
  "stage": "funding stage e.g. Seed, Series A, Series B etc",
  "valuation": numeric valuation in millions or null,
  "round_size": numeric round size in millions or null,
  "lead_investor": "lead investor name or null",
  "hq": "city, country or null",
  "website": "website url or null",
  "notes": "2-3 sentence summary of what the company does and their key value proposition"
}"""}
            ]
        }]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw)


def extract_portfolio_from_pdf(pdf_bytes):
    """Extract portfolio company metrics from board decks, financial reports, investor updates."""
    client = get_client()
    b64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    resp = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1500,
        system="Extract financial and operational metrics from this document. Return ONLY valid JSON, no markdown.",
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": b64}},
                {"type": "text", "text": """Extract all available portfolio company metrics and return this JSON (use null for missing fields):
{
  "company": "company name",
  "sector": "best matching: AI/ML, Fintech, Healthcare, SaaS, Consumer, Deeptech, Other",
  "stage": "current stage e.g. Series A, Series B, Growth",
  "revenue": numeric annual revenue in millions or null,
  "revenue_growth": numeric YoY growth percentage or null,
  "arr": numeric ARR in millions or null,
  "burn_rate": numeric monthly burn in millions or null,
  "runway_months": numeric runway in months or null,
  "employees": numeric headcount or null,
  "current_valuation": numeric valuation in millions or null,
  "notes": "2-3 sentence summary of company status and key highlights from this report"
}"""}
            ]
        }]
    )
    raw = resp.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"): raw = raw[4:]
    return json.loads(raw)


def clean_num(val, default=0.0):
    """Safely convert extracted value to float."""
    try:
        return float(val) if val is not None else default
    except:
        return default


# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "◈  Market Analysis",
    "◈  Financial Modeling",
    "◈  Pitch Deck Analyzer",
    "◈  Deal Flow",
    "◈  Portfolio",
    "◈  Comparable Deals",
    "◈  Scenario Tester",
    "◈  VC / PE News",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — MARKET ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-label">Deep Market Intelligence</div>', unsafe_allow_html=True)
    col_input, col_type = st.columns([3, 1])
    with col_input:
        market_query = st.text_input("Market or Company", placeholder="e.g. 'AI Infrastructure', 'Fintech Lending', 'Stripe'", key="market_input")
    with col_type:
        analysis_type = st.selectbox("Analysis Focus", ["Full Market Deep-Dive", "Competitive Landscape", "Investment Opportunity", "Company Profile"])

    analysis_sections = st.multiselect(
        "Include Sections",
        ["TAM / SAM / SOM", "Key Players & Moats", "Funding & Deal Activity", "Growth Drivers & Tailwinds",
         "Risks & Headwinds", "Regulatory Environment", "Exit Opportunities", "VC/PE Thesis"],
        default=["TAM / SAM / SOM", "Key Players & Moats", "Funding & Deal Activity", "Growth Drivers & Tailwinds", "Risks & Headwinds", "VC/PE Thesis"],
    )

    if st.button("▶  Run Deep Analysis", key="run_market") and market_query:
        sections_str = ", ".join(analysis_sections)
        system = """You are a senior partner at a top-tier VC/PE firm. Provide institutional-grade analysis 
        with specific data, numbers, company names, and actionable insights. Use markdown with clear ## headers."""
        prompt = f"""Conduct a comprehensive {analysis_type} for: **{market_query}**
Search for current data. Cover: {sections_str}.
Include: specific market sizes, named companies with recent rounds/amounts, CAGR figures, investment thesis points.
End with **Investment Verdict** scoring VC fit (1-10) and PE fit (1-10)."""
        with st.spinner("Researching markets…"):
            try:
                result = stream_claude(prompt, system, use_search=True)
                st.session_state["market_result"] = result
                st.session_state["market_query_done"] = market_query
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    if "market_result" in st.session_state:
        st.markdown(f'<div class="section-label">Analysis: {st.session_state.get("market_query_done","")}</div>', unsafe_allow_html=True)
        st.markdown(st.session_state["market_result"])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — FINANCIAL MODELING
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Financial Modeling Suite</div>', unsafe_allow_html=True)
    model_type = st.selectbox("Select Model", ["VC Method (Pre-Money Valuation)", "DCF Analysis", "LBO Model", "Comparable Company Analysis (Comps)"], key="model_type")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    if model_type == "VC Method (Pre-Money Valuation)":
        c1, c2, c3 = st.columns(3)
        with c1:
            vc_co = st.text_input("Company Name", "Acme AI", key="vc_co")
            revenue_exit = st.number_input("Projected Revenue at Exit ($M)", value=100.0, step=5.0)
            ebitda_margin = st.slider("EBITDA Margin at Exit (%)", 5, 60, 25)
        with c2:
            revenue_multiple = st.number_input("Exit EV/Revenue Multiple (x)", value=8.0, step=0.5)
            ebitda_multiple = st.number_input("Exit EV/EBITDA Multiple (x)", value=15.0, step=0.5)
            years_to_exit = st.number_input("Years to Exit", value=5, step=1, min_value=1, max_value=15)
        with c3:
            target_ror = st.slider("Target IRR (%)", 20, 60, 30)
            investment_amount = st.number_input("Investment Amount ($M)", value=10.0, step=1.0)
            current_shares = st.number_input("Pre-Investment Shares (M)", value=10.0, step=0.5)

        if st.button("▶  Calculate VC Valuation"):
            ebitda_exit = revenue_exit * (ebitda_margin / 100)
            ev_rev = revenue_exit * revenue_multiple
            ev_ebitda = ebitda_exit * ebitda_multiple
            ev_blend = (ev_rev + ev_ebitda) / 2
            moic = (1 + target_ror / 100) ** years_to_exit
            post = ev_blend / moic
            pre = post - investment_amount
            own = (investment_amount / post) * 100
            new_sh = (own / (100 - own)) * current_shares
            pps = investment_amount / new_sh if new_sh > 0 else 0
            ret = investment_amount * moic
            st.session_state["vc_r"] = dict(pre=pre, post=post, own=own, moic=moic, ev=ev_blend, new_sh=new_sh, pps=pps, ret=ret, co=vc_co, inv=investment_amount)

        if "vc_r" in st.session_state:
            r = st.session_state["vc_r"]
            st.markdown(f'<div class="section-label">Results — {r["co"]}</div>', unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            for col, lbl, val in zip([c1,c2,c3,c4], ["Pre-Money","Post-Money","Ownership %","MOIC Needed"],
                                     [f"${r['pre']:.1f}M", f"${r['post']:.1f}M", f"{r['own']:.1f}%", f"{r['moic']:.1f}x"]):
                with col: st.markdown(f'<div class="metric-pill"><div class="label">{lbl}</div><div class="val">{val}</div></div>', unsafe_allow_html=True)
            fig = go.Figure(go.Waterfall(orientation="v", measure=["absolute","relative","total"],
                x=["Investment","Value Creation","Exit Value"], y=[r["inv"], r["ev"]-r["inv"], 0],
                connector={"line":{"color":"#1e2130"}},
                increasing={"marker":{"color":"#3ecfb2"}}, totals={"marker":{"color":"#c9a84c"}}))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=11), margin=dict(l=10,r=10,t=30,b=10), height=260,
                yaxis=dict(gridcolor="#1e2130", title="$M"), xaxis=dict(gridcolor="#1e2130"))
            st.plotly_chart(fig, use_container_width=True)

    elif model_type == "DCF Analysis":
        c1, c2, c3 = st.columns(3)
        with c1:
            dcf_co = st.text_input("Company", "Portfolio Co.", key="dcf_co")
            base_rev = st.number_input("Current Revenue ($M)", value=50.0, step=5.0)
            rg13 = st.slider("Rev Growth Yr 1-3 (%)", 0, 100, 30)
        with c2:
            rg47 = st.slider("Rev Growth Yr 4-7 (%)", 0, 60, 15)
            ebitda_dcf = st.slider("EBITDA Margin (%)", -20, 60, 20)
            capex_pct = st.slider("CapEx % of Revenue", 0, 30, 5)
        with c3:
            tax_rate = st.slider("Tax Rate (%)", 0, 40, 25)
            wacc = st.slider("WACC (%)", 5, 30, 12)
            tgr = st.slider("Terminal Growth Rate (%)", 1, 6, 3)

        if st.button("▶  Build DCF Model"):
            yrs = list(range(1,8)); revs=[]; fcfs=[]
            rev = base_rev
            for y in yrs:
                g = rg13/100 if y<=3 else rg47/100
                rev = rev*(1+g)
                ebitda = rev*(ebitda_dcf/100)
                nopat = ebitda*(1-tax_rate/100)
                fcf = nopat - rev*(capex_pct/100)
                revs.append(rev); fcfs.append(fcf)
            dfs = [(1/(1+wacc/100)**y) for y in yrs]
            pv_fcfs = [f*d for f,d in zip(fcfs,dfs)]
            tv = fcfs[-1]*(1+tgr/100)/((wacc-tgr)/100)
            pv_tv = tv*dfs[-1]
            ev = sum(pv_fcfs)+pv_tv
            st.session_state["dcf_r"] = dict(yrs=yrs, revs=revs, fcfs=fcfs, pv_fcfs=pv_fcfs, tv=tv, pv_tv=pv_tv, ev=ev, co=dcf_co)

        if "dcf_r" in st.session_state:
            r = st.session_state["dcf_r"]
            st.markdown(f'<div class="section-label">DCF Results — {r["co"]}</div>', unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            for col, lbl, val in zip([c1,c2,c3],["Enterprise Value","PV of FCFs","PV Terminal Value"],
                                     [f"${r['ev']:.1f}M", f"${sum(r['pv_fcfs']):.1f}M", f"${r['pv_tv']:.1f}M"]):
                with col: st.markdown(f'<div class="metric-pill"><div class="label">{lbl}</div><div class="val">{val}</div></div>', unsafe_allow_html=True)
            df = pd.DataFrame({"Year":[f"Yr {y}" for y in r["yrs"]], "Revenue":r["revs"], "FCF":r["fcfs"], "PV FCF":r["pv_fcfs"]})
            fig = make_subplots(specs=[[{"secondary_y":True}]])
            fig.add_trace(go.Bar(x=df.Year, y=df.Revenue, name="Revenue", marker_color="#1e2130"))
            fig.add_trace(go.Scatter(x=df.Year, y=df.FCF, name="FCF", line=dict(color="#3ecfb2",width=2), mode="lines+markers"))
            fig.add_trace(go.Scatter(x=df.Year, y=df["PV FCF"], name="PV FCF", line=dict(color="#c9a84c",width=2,dash="dot"), mode="lines+markers"))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
                legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=10,t=30,b=10), height=280,
                yaxis=dict(gridcolor="#1e2130",title="$M"), xaxis=dict(gridcolor="#1e2130"))
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df.set_index("Year").round(1), use_container_width=True)

    elif model_type == "LBO Model":
        c1, c2, c3 = st.columns(3)
        with c1:
            lbo_co = st.text_input("Company", "Target Co.", key="lbo_co")
            entry_ebitda = st.number_input("LTM EBITDA ($M)", value=50.0, step=5.0)
            entry_mult = st.number_input("Entry EV/EBITDA (x)", value=10.0, step=0.5)
        with c2:
            debt_pct = st.slider("Debt % of Purchase Price", 40, 80, 60)
            int_rate = st.slider("Interest Rate (%)", 4, 15, 7)
            ebitda_g = st.slider("Annual EBITDA Growth (%)", 0, 30, 10)
        with c3:
            exit_mult = st.number_input("Exit EV/EBITDA (x)", value=11.0, step=0.5)
            hold_pe = st.number_input("Hold Period (Years)", value=5, step=1, min_value=2, max_value=10)
            amort_pct = st.slider("Annual Debt Paydown (%)", 5, 25, 10)

        if st.button("▶  Build LBO Model"):
            pp = entry_ebitda * entry_mult
            debt = pp * (debt_pct/100)
            eq_in = pp * (1-debt_pct/100)
            yrs = list(range(1, int(hold_pe)+1))
            ebitda_p, debt_b, eq_v = [], [], []
            e = entry_ebitda; d = debt
            for y in yrs:
                e = e*(1+ebitda_g/100)
                d = max(0, d - debt*(amort_pct/100))
                ev = e*exit_mult
                eq_v.append(ev-d); ebitda_p.append(e); debt_b.append(d)
            moic = eq_v[-1]/eq_in if eq_in>0 else 0
            irr = (moic**(1/hold_pe)-1)*100
            st.session_state["lbo_r"] = dict(pp=pp, debt=debt, eq_in=eq_in, moic=moic, irr=irr, yrs=yrs, ebitda_p=ebitda_p, debt_b=debt_b, eq_v=eq_v, co=lbo_co)

        if "lbo_r" in st.session_state:
            r = st.session_state["lbo_r"]
            st.markdown(f'<div class="section-label">LBO Results — {r["co"]}</div>', unsafe_allow_html=True)
            c1,c2,c3,c4 = st.columns(4)
            for col, lbl, val, good in zip([c1,c2,c3,c4],
                ["Purchase Price","Equity In","MOIC","IRR"],
                [f"${r['pp']:.1f}M", f"${r['eq_in']:.1f}M", f"{r['moic']:.2f}x", f"{r['irr']:.1f}%"],
                [None, None, r['moic']>=2.5, r['irr']>=20]):
                cls = "" if good is None else ("positive" if good else "negative")
                with col: st.markdown(f'<div class="metric-pill"><div class="label">{lbl}</div><div class="val {cls}">{val}</div></div>', unsafe_allow_html=True)
            fig = make_subplots(rows=1, cols=2, subplot_titles=("EBITDA & Equity Value ($M)","Debt Paydown ($M)"))
            yrl = [f"Yr {y}" for y in r["yrs"]]
            fig.add_trace(go.Bar(x=yrl, y=r["ebitda_p"], name="EBITDA", marker_color="#1e2130"), row=1, col=1)
            fig.add_trace(go.Scatter(x=yrl, y=r["eq_v"], name="Equity Value", line=dict(color="#c9a84c",width=2), mode="lines+markers"), row=1, col=1)
            fig.add_trace(go.Bar(x=yrl, y=r["debt_b"], name="Debt Balance", marker_color="#e05c5c"), row=1, col=2)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
                legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=10,t=40,b=10), height=300)
            st.plotly_chart(fig, use_container_width=True)

    elif model_type == "Comparable Company Analysis (Comps)":
        target_co = st.text_input("Target Company", "Target Co.", key="comps_target")
        st.markdown("**Enter Comparable Companies (up to 5)**")
        comp_data = []
        for i in range(5):
            cc = st.columns(5)
            name = cc[0].text_input(f"Company {i+1}", key=f"cn_{i}", placeholder=f"Comp {i+1}")
            rev = cc[1].number_input(f"Revenue ($M)", key=f"cr_{i}", value=0.0)
            eb = cc[2].number_input(f"EBITDA ($M)", key=f"ce_{i}", value=0.0)
            ev = cc[3].number_input(f"EV ($M)", key=f"cv_{i}", value=0.0)
            g = cc[4].number_input(f"Growth (%)", key=f"cg_{i}", value=0.0)
            if name: comp_data.append({"Company":name,"Revenue":rev,"EBITDA":eb,"EV":ev,"Growth":g})
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        tc1, tc2 = st.columns(2)
        t_rev = tc1.number_input("Target Revenue ($M)", value=30.0)
        t_ebitda = tc2.number_input("Target EBITDA ($M)", value=8.0)

        if st.button("▶  Run Comps") and comp_data:
            df = pd.DataFrame(comp_data)
            df = df[df["Revenue"]>0].copy()
            df["EV/Rev"] = df.apply(lambda r: round(r["EV"]/r["Revenue"],1) if r["Revenue"]>0 else None, axis=1)
            df["EV/EBITDA"] = df.apply(lambda r: round(r["EV"]/r["EBITDA"],1) if r["EBITDA"]>0 else None, axis=1)
            med_rev = df["EV/Rev"].median()
            med_eb = df["EV/EBITDA"].median()
            imp_rev = t_rev*med_rev if not math.isnan(med_rev) else 0
            imp_eb = t_ebitda*med_eb if not math.isnan(med_eb) else 0
            blend = (imp_rev+imp_eb)/2 if imp_eb>0 else imp_rev
            st.session_state["comps_r"] = dict(df=df, med_rev=med_rev, med_eb=med_eb, imp_rev=imp_rev, imp_eb=imp_eb, blend=blend, target=target_co)

        if "comps_r" in st.session_state:
            r = st.session_state["comps_r"]
            c1,c2,c3 = st.columns(3)
            for col, lbl, val in zip([c1,c2,c3],["Median EV/Rev","Implied EV (Rev)","Blended EV"],
                                     [f"{r['med_rev']:.1f}x", f"${r['imp_rev']:.1f}M", f"${r['blend']:.1f}M"]):
                with col: st.markdown(f'<div class="metric-pill"><div class="label">{lbl}</div><div class="val">{val}</div></div>', unsafe_allow_html=True)
            st.dataframe(r["df"].set_index("Company"), use_container_width=True)
            if not r["df"].empty:
                fig = go.Figure(go.Bar(x=r["df"]["Company"], y=r["df"]["EV/Rev"], marker_color="#c9a84c"))
                fig.add_hline(y=r["med_rev"], line_dash="dot", line_color="#3ecfb2", annotation_text="Median")
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
                    margin=dict(l=10,r=10,t=30,b=10), height=260,
                    yaxis=dict(gridcolor="#1e2130",title="EV/Rev"), xaxis=dict(gridcolor="#1e2130"))
                st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — PITCH DECK ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-label">Pitch Deck Analyzer</div>', unsafe_allow_html=True)

    col_up, col_info = st.columns([2, 1])
    with col_up:
        uploaded_deck = st.file_uploader("Upload Pitch Deck (PDF)", type=["pdf"], key="deck_upload")
    with col_info:
        deck_company = st.text_input("Company Name (optional)", key="deck_company")
        st.markdown('<div style="font-size:0.75rem; color:#4a5075; margin-top:0.5rem;">Claude will extract market size, team quality, product strength, financials, and risk factors — then generate a full investment memo.</div>', unsafe_allow_html=True)

    if st.button("▶  Analyze Pitch Deck", key="run_deck") and uploaded_deck:
        with st.spinner("Reading deck and generating investment memo…"):
            try:
                pdf_bytes = uploaded_deck.read()
                co_name = deck_company or uploaded_deck.name.replace(".pdf","")
                result = analyze_pdf_with_claude(pdf_bytes, co_name)
                st.session_state["deck_result"] = result

                # Save to DB
                conn = sqlite3.connect("alphalens.db")
                conn.execute("""INSERT INTO pitch_decks (company, date_analyzed, overall_score, market_score,
                    team_score, product_score, financial_score, risk_score, full_analysis, investment_verdict)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (result.get("company_name","Unknown"), datetime.now().strftime("%Y-%m-%d"),
                     result["scores"]["overall"], result["scores"]["market"],
                     result["scores"]["team"], result["scores"]["product"],
                     result["scores"]["financials"], result["scores"]["risk"],
                     json.dumps(result), result["investment_verdict"]))
                conn.commit(); conn.close()
            except Exception as e:
                st.error(f"Analysis failed: {e}")

    if "deck_result" in st.session_state:
        r = st.session_state["deck_result"]
        scores = r.get("scores", {})

        st.markdown(f'<div class="section-label">{r.get("company_name","Company")} — {r.get("one_liner","")}</div>', unsafe_allow_html=True)

        # Verdict banner
        verdict = r.get("investment_verdict","")
        v_class = "verdict-pass" if "STRONG" in verdict else ("verdict-pass-soft" if verdict in ["PASS","PASS WITH CONDITIONS","SOFT PASS"] else "verdict-fail")
        st.markdown(f'<div class="{v_class}">◈ VERDICT: {verdict}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.85rem; color:#8890b8; margin-top:0.5rem; margin-bottom:1rem;">{r.get("verdict_reasoning","")}</div>', unsafe_allow_html=True)

        # Score cards
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        score_items = [
            (c1, "Overall", scores.get("overall",0)),
            (c2, "Market", scores.get("market",0)),
            (c3, "Team", scores.get("team",0)),
            (c4, "Product", scores.get("product",0)),
            (c5, "Financials", scores.get("financials",0)),
            (c6, "Risk Profile", scores.get("risk",0)),
        ]
        for col, lbl, val in score_items:
            color = "#3ecfb2" if val>=75 else ("#c9a84c" if val>=50 else "#e05c5c")
            with col:
                st.markdown(f"""<div class="metric-pill">
                    <div class="label">{lbl}</div>
                    <div class="val" style="color:{color}">{val}</div>
                    <div class="score-bar-wrap"><div class="score-bar" style="width:{val}%;background:{color}"></div></div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Radar chart
        categories = ["Market","Team","Product","Financials","Risk"]
        vals = [scores.get("market",0), scores.get("team",0), scores.get("product",0), scores.get("financials",0), scores.get("risk",0)]
        fig = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=categories+[categories[0]],
            fill='toself', fillcolor='rgba(201,168,76,0.15)', line=dict(color='#c9a84c', width=2)))
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)',
            radialaxis=dict(visible=True, range=[0,100], gridcolor='#1e2130', color='#4a5075'),
            angularaxis=dict(color='#8890b8')),
            paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=30,r=30,t=30,b=30), height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Detailed sections
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-label">Market Analysis</div>', unsafe_allow_html=True)
            ms = r.get("market_size", {})
            st.markdown(f"""<div class="card">
                <div style="font-size:0.8rem; color:#8890b8;">TAM: <span style="color:#e8c97a">{ms.get('tam','—')}</span> &nbsp;|&nbsp;
                SAM: <span style="color:#e8c97a">{ms.get('sam','—')}</span> &nbsp;|&nbsp;
                SOM: <span style="color:#e8c97a">{ms.get('som','—')}</span></div>
                <div style="font-size:0.82rem; color:#d4d8f0; margin-top:0.6rem;">{ms.get('assessment','')}</div>
            </div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-label">Team</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card" style="font-size:0.82rem; color:#d4d8f0;">{r.get("team_analysis","")}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Key Strengths</div>', unsafe_allow_html=True)
            for s in r.get("key_strengths", []):
                st.markdown(f'<div style="font-size:0.82rem; color:#3ecfb2; padding:3px 0;">✓ {s}</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="section-label">Product & Technology</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card" style="font-size:0.82rem; color:#d4d8f0;">{r.get("product_analysis","")}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-label">Key Risks</div>', unsafe_allow_html=True)
            for risk in r.get("key_risks", []):
                st.markdown(f'<div style="font-size:0.82rem; color:#e05c5c; padding:3px 0;">⚠ {risk}</div>', unsafe_allow_html=True)

            if r.get("red_flags"):
                st.markdown('<div class="section-label">Red Flags</div>', unsafe_allow_html=True)
                for flag in r.get("red_flags", []):
                    st.markdown(f'<div style="font-size:0.82rem; color:#e05c5c; font-weight:600; padding:3px 0;">🚩 {flag}</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-label">Next Steps</div>', unsafe_allow_html=True)
        ns_cols = st.columns(len(r.get("next_steps",[])) or 1)
        for i, step in enumerate(r.get("next_steps",[])):
            with ns_cols[i]:
                st.markdown(f'<div class="metric-pill"><div class="label">Step {i+1}</div><div style="font-size:0.8rem; color:#d4d8f0; margin-top:4px;">{step}</div></div>', unsafe_allow_html=True)

    # Past analyses
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Past Analyses</div>', unsafe_allow_html=True)
    conn = sqlite3.connect("alphalens.db")
    past = pd.read_sql("SELECT company, date_analyzed, overall_score, investment_verdict FROM pitch_decks ORDER BY id DESC LIMIT 20", conn)
    conn.close()
    if not past.empty:
        st.dataframe(past, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — DEAL FLOW TRACKER
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-label">Deal Flow Tracker</div>', unsafe_allow_html=True)

    with st.expander("➕  Add New Deal", expanded=False):
        st.markdown('<div style="font-size:0.8rem; color:#8890b8; margin-bottom:0.8rem;">Drop a pitch deck or one-pager to auto-fill fields, or enter manually below.</div>', unsafe_allow_html=True)

        deal_pdf = st.file_uploader("📄 Auto-fill from PDF (pitch deck / one-pager)", type=["pdf"], key="deal_pdf_upload")
        if deal_pdf and st.button("▶  Extract from PDF", key="extract_deal_pdf"):
            with st.spinner("Reading document and extracting deal info…"):
                try:
                    extracted = extract_deal_from_pdf(deal_pdf.read())
                    st.session_state["deal_prefill"] = extracted
                    st.success(f"✓ Extracted info for: {extracted.get('company','Unknown')} — review and save below")
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

        pf = st.session_state.get("deal_prefill", {})
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        d1, d2, d3 = st.columns(3)
        with d1:
            df_co = st.text_input("Company Name", value=pf.get("company",""), key="df_co")
            sector_opts = ["AI/ML","Fintech","Healthcare","SaaS","Consumer","Deeptech","Crypto/Web3","Climate","Biotech","Other"]
            pf_sector = pf.get("sector","AI/ML")
            pf_sector_idx = sector_opts.index(pf_sector) if pf_sector in sector_opts else 0
            df_sector = st.selectbox("Sector", sector_opts, index=pf_sector_idx, key="df_sector")
            stage_opts = ["Pre-Seed","Seed","Series A","Series B","Series C","Growth","PE Buyout","Other"]
            pf_stage = pf.get("stage","Seed")
            pf_stage_idx = next((i for i,s in enumerate(stage_opts) if pf_stage and pf_stage.lower() in s.lower()), 1)
            df_stage = st.selectbox("Stage", stage_opts, index=pf_stage_idx, key="df_stage")
        with d2:
            df_val = st.number_input("Valuation ($M)", value=clean_num(pf.get("valuation")), step=1.0, key="df_val")
            df_round = st.number_input("Round Size ($M)", value=clean_num(pf.get("round_size")), step=0.5, key="df_round")
            df_lead = st.text_input("Lead Investor", value=pf.get("lead_investor","") or "", key="df_lead")
        with d3:
            df_score = st.slider("Internal Score (1-10)", 1, 10, 5, key="df_score")
            df_status = st.selectbox("Status", ["Screening","In Diligence","Term Sheet","Passed","Invested","Portfolio","Exited"], key="df_status")
            df_hq = st.text_input("HQ Location", value=pf.get("hq","") or "", key="df_hq")
        df_notes = st.text_area("Notes / Thesis", value=pf.get("notes","") or "", key="df_notes", height=80)
        df_website = st.text_input("Website", value=pf.get("website","") or "", key="df_website")

        if st.button("▶  Add to Deal Flow", key="add_deal"):
            if df_co:
                conn = sqlite3.connect("alphalens.db")
                conn.execute("""INSERT INTO deal_flow (company,sector,stage,valuation,round_size,lead_investor,
                    score,status,notes,date_added,website,hq) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (df_co, df_sector, df_stage, df_val, df_round, df_lead, df_score, df_status,
                     df_notes, date.today().isoformat(), df_website, df_hq))
                conn.commit(); conn.close()
                st.session_state.pop("deal_prefill", None)
                st.success(f"✓ {df_co} added to deal flow")
                st.rerun()

    # Filters
    f1, f2, f3 = st.columns(3)
    with f1: filt_sector = st.selectbox("Filter by Sector", ["All","AI/ML","Fintech","Healthcare","SaaS","Consumer","Deeptech","Crypto/Web3","Climate","Biotech","Other"], key="filt_sector")
    with f2: filt_stage = st.selectbox("Filter by Stage", ["All","Pre-Seed","Seed","Series A","Series B","Series C","Growth","PE Buyout","Other"], key="filt_stage")
    with f3: filt_status = st.selectbox("Filter by Status", ["All","Screening","In Diligence","Term Sheet","Passed","Invested","Portfolio","Exited"], key="filt_status")

    conn = sqlite3.connect("alphalens.db")
    query = "SELECT * FROM deal_flow WHERE 1=1"
    if filt_sector != "All": query += f" AND sector='{filt_sector}'"
    if filt_stage != "All": query += f" AND stage='{filt_stage}'"
    if filt_status != "All": query += f" AND status='{filt_status}'"
    query += " ORDER BY id DESC"
    deals_df = pd.read_sql(query, conn)
    conn.close()

    if not deals_df.empty:
        # Summary metrics
        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-pill"><div class="label">Total Deals</div><div class="val">{len(deals_df)}</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-pill"><div class="label">Avg Score</div><div class="val">{deals_df["score"].mean():.1f}/10</div></div>', unsafe_allow_html=True)
        with c3:
            invested = deals_df[deals_df["status"]=="Invested"]["round_size"].sum()
            st.markdown(f'<div class="metric-pill"><div class="label">Invested ($M)</div><div class="val">${invested:.1f}M</div></div>', unsafe_allow_html=True)
        with c4:
            pipeline = len(deals_df[deals_df["status"].isin(["Screening","In Diligence","Term Sheet"])])
            st.markdown(f'<div class="metric-pill"><div class="label">Active Pipeline</div><div class="val">{pipeline}</div></div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # Deal cards
        for _, row in deals_df.iterrows():
            score_color = "#3ecfb2" if row["score"]>=8 else ("#c9a84c" if row["score"]>=5 else "#e05c5c")
            status_colors = {"Invested":"#3ecfb2","Portfolio":"#c9a84c","In Diligence":"#60a5fa","Term Sheet":"#a78bfa","Passed":"#4a5075","Exited":"#e8c97a","Screening":"#8890b8"}
            sc = status_colors.get(row["status"],"#8890b8")
            st.markdown(f"""<div class="deal-row">
              <div>
                <div class="deal-company">{row['company']}</div>
                <div class="deal-meta">{row['sector']} · {row['stage']} · {row['hq'] or '—'} · Added {row['date_added']}</div>
                {f'<div style="font-size:0.78rem; color:#8890b8; margin-top:4px;">{row["notes"][:120]}{"..." if len(str(row["notes"]))>120 else ""}</div>' if row['notes'] else ''}
              </div>
              <div style="text-align:right; min-width:180px;">
                <div style="font-family:IBM Plex Mono; font-size:1rem; font-weight:600; color:#f0f2ff;">${row['valuation']:.0f}M</div>
                <div style="font-family:IBM Plex Mono; font-size:0.7rem; color:#8890b8;">Round: ${row['round_size']:.0f}M</div>
                <div style="margin-top:6px;">
                  <span style="font-family:IBM Plex Mono; font-size:0.65rem; color:{score_color}; border:1px solid {score_color}; padding:2px 6px; border-radius:2px;">{row['score']}/10</span>
                  &nbsp;
                  <span style="font-family:IBM Plex Mono; font-size:0.65rem; color:{sc}; border:1px solid {sc}; padding:2px 6px; border-radius:2px;">{row['status']}</span>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Pipeline funnel chart
        st.markdown('<div class="section-label">Pipeline Funnel</div>', unsafe_allow_html=True)
        funnel_data = deals_df["status"].value_counts().reindex(["Screening","In Diligence","Term Sheet","Invested","Portfolio","Exited","Passed"], fill_value=0)
        fig = go.Figure(go.Funnel(y=funnel_data.index.tolist(), x=funnel_data.values.tolist(),
            marker=dict(color=["#8890b8","#60a5fa","#a78bfa","#3ecfb2","#c9a84c","#e8c97a","#4a5075"]),
            textinfo="value+percent initial"))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
            margin=dict(l=10,r=10,t=20,b=10), height=300)
        st.plotly_chart(fig, use_container_width=True)

        # Delete option
        with st.expander("🗑  Delete a Deal"):
            del_id = st.number_input("Deal ID to delete", min_value=1, step=1, key="del_id")
            if st.button("Delete", key="del_deal"):
                conn = sqlite3.connect("alphalens.db")
                conn.execute("DELETE FROM deal_flow WHERE id=?", (int(del_id),))
                conn.commit(); conn.close()
                st.rerun()
    else:
        st.markdown('<div class="card" style="text-align:center; padding:3rem;"><div style="font-family:IBM Plex Mono; color:#4a5075; font-size:0.8rem; letter-spacing:2px;">NO DEALS IN PIPELINE YET — ADD YOUR FIRST DEAL ABOVE</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — PORTFOLIO MONITORING
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-label">Portfolio Monitoring Dashboard</div>', unsafe_allow_html=True)

    with st.expander("➕  Add / Update Portfolio Company", expanded=False):
        st.markdown('<div style="font-size:0.8rem; color:#8890b8; margin-bottom:0.8rem;">Drop a board deck, investor update, or financial report to auto-fill metrics, or enter manually below.</div>', unsafe_allow_html=True)

        port_pdf = st.file_uploader("📄 Auto-fill from PDF (board deck / investor update)", type=["pdf"], key="port_pdf_upload")
        if port_pdf and st.button("▶  Extract from PDF", key="extract_port_pdf"):
            with st.spinner("Reading document and extracting metrics…"):
                try:
                    extracted = extract_portfolio_from_pdf(port_pdf.read())
                    st.session_state["port_prefill"] = extracted
                    st.success(f"✓ Extracted metrics for: {extracted.get('company','Unknown')} — review and save below")
                except Exception as e:
                    st.error(f"Extraction failed: {e}")

        ppf = st.session_state.get("port_prefill", {})
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        p1, p2, p3 = st.columns(3)
        with p1:
            p_co = st.text_input("Company Name", value=ppf.get("company",""), key="p_co")
            sector_opts_p = ["AI/ML","Fintech","Healthcare","SaaS","Consumer","Deeptech","Other"]
            ppf_sector = ppf.get("sector","AI/ML")
            ppf_sector_idx = sector_opts_p.index(ppf_sector) if ppf_sector in sector_opts_p else 0
            p_sector = st.selectbox("Sector", sector_opts_p, index=ppf_sector_idx, key="p_sector")
            p_inv_date = st.date_input("Investment Date", key="p_inv_date")
        with p2:
            p_invested = st.number_input("Amount Invested ($M)", value=0.0, step=0.5, key="p_invested")
            p_cur_val = st.number_input("Current Valuation ($M)", value=clean_num(ppf.get("current_valuation")), step=1.0, key="p_cur_val")
            p_own = st.number_input("Ownership (%)", value=0.0, step=0.5, key="p_own")
        with p3:
            p_rev = st.number_input("Annual Revenue ($M)", value=clean_num(ppf.get("revenue")), step=0.5, key="p_rev")
            p_rev_g = st.number_input("Revenue Growth YoY (%)", value=clean_num(ppf.get("revenue_growth")), step=1.0, key="p_rev_g")
            p_burn = st.number_input("Monthly Burn Rate ($M)", value=clean_num(ppf.get("burn_rate")), step=0.1, key="p_burn")
        p4, p5 = st.columns(2)
        with p4:
            p_runway = st.number_input("Runway (Months)", value=clean_num(ppf.get("runway_months")), step=1.0, key="p_runway")
            p_arr = st.number_input("ARR ($M)", value=clean_num(ppf.get("arr")), step=0.5, key="p_arr")
        with p5:
            p_emp = st.number_input("Employees", value=int(clean_num(ppf.get("employees"))), step=5, key="p_emp")
            stage_opts_p = ["Seed","Series A","Series B","Series C","Growth","Pre-IPO"]
            ppf_stage = ppf.get("stage","Series A")
            ppf_stage_idx = next((i for i,s in enumerate(stage_opts_p) if ppf_stage and ppf_stage.lower() in s.lower()), 1)
            p_stage = st.selectbox("Current Stage", stage_opts_p, index=ppf_stage_idx, key="p_stage")
        p_notes = st.text_area("Notes", value=ppf.get("notes","") or "", key="p_notes", height=60)

        if st.button("▶  Save to Portfolio", key="save_portfolio"):
            if p_co:
                conn = sqlite3.connect("alphalens.db")
                conn.execute("""INSERT INTO portfolio (company,sector,investment_date,invested_amount,
                    current_valuation,ownership_pct,revenue,revenue_growth,burn_rate,runway_months,
                    arr,employees,stage,notes,last_updated) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (p_co, p_sector, str(p_inv_date), p_invested, p_cur_val, p_own, p_rev, p_rev_g,
                     p_burn, p_runway, p_arr, p_emp, p_stage, p_notes, date.today().isoformat()))
                conn.commit(); conn.close()
                st.session_state.pop("port_prefill", None)
                st.success(f"✓ {p_co} added to portfolio")
                st.rerun()

    conn = sqlite3.connect("alphalens.db")
    port_df = pd.read_sql("SELECT * FROM portfolio ORDER BY id DESC", conn)
    conn.close()

    if not port_df.empty:
        # Top metrics
        total_invested = port_df["invested_amount"].sum()
        total_val = (port_df["current_valuation"] * port_df["ownership_pct"] / 100).sum()
        moic_overall = total_val / total_invested if total_invested > 0 else 0
        avg_runway = port_df[port_df["runway_months"]>0]["runway_months"].mean()

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.markdown(f'<div class="metric-pill"><div class="label">Total Invested</div><div class="val">${total_invested:.1f}M</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="metric-pill"><div class="label">Portfolio Value</div><div class="val">${total_val:.1f}M</div></div>', unsafe_allow_html=True)
        with c3:
            mc = "positive" if moic_overall>=2 else ("" if moic_overall>=1 else "negative")
            st.markdown(f'<div class="metric-pill"><div class="label">Blended MOIC</div><div class="val {mc}">{moic_overall:.2f}x</div></div>', unsafe_allow_html=True)
        with c4:
            rc = "positive" if avg_runway>=18 else ("" if avg_runway>=12 else "negative")
            st.markdown(f'<div class="metric-pill"><div class="label">Avg Runway</div><div class="val {rc}">{avg_runway:.0f} mo</div></div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Portfolio Companies</div>', unsafe_allow_html=True)

        for _, row in port_df.iterrows():
            implied_val = row["current_valuation"] * row["ownership_pct"] / 100 if row["ownership_pct"] > 0 else 0
            moic = implied_val / row["invested_amount"] if row["invested_amount"] > 0 else 0
            moic_color = "#3ecfb2" if moic>=2 else ("#c9a84c" if moic>=1 else "#e05c5c")
            runway_color = "#3ecfb2" if row["runway_months"]>=18 else ("#c9a84c" if row["runway_months"]>=12 else "#e05c5c")

            st.markdown(f"""<div class="deal-row" style="align-items:flex-start;">
              <div style="flex:1">
                <div class="deal-company">{row['company']}</div>
                <div class="deal-meta">{row['sector']} · {row['stage']} · Invested {row['investment_date']}</div>
                <div style="display:flex; gap:1.5rem; margin-top:0.6rem; flex-wrap:wrap;">
                  <div style="font-size:0.75rem;"><span style="color:#4a5075;">ARR</span> <span style="color:#e8c97a; font-family:IBM Plex Mono;">${row['arr']:.1f}M</span></div>
                  <div style="font-size:0.75rem;"><span style="color:#4a5075;">Growth</span> <span style="color:#3ecfb2; font-family:IBM Plex Mono;">{row['revenue_growth']:.0f}%</span></div>
                  <div style="font-size:0.75rem;"><span style="color:#4a5075;">Burn</span> <span style="color:#e05c5c; font-family:IBM Plex Mono;">${row['burn_rate']:.1f}M/mo</span></div>
                  <div style="font-size:0.75rem;"><span style="color:#4a5075;">Runway</span> <span style="color:{runway_color}; font-family:IBM Plex Mono;">{row['runway_months']:.0f} mo</span></div>
                  <div style="font-size:0.75rem;"><span style="color:#4a5075;">Employees</span> <span style="color:#d4d8f0; font-family:IBM Plex Mono;">{row['employees']}</span></div>
                </div>
              </div>
              <div style="text-align:right; min-width:200px;">
                <div style="font-family:IBM Plex Mono; font-size:0.7rem; color:#8890b8;">Invested: ${row['invested_amount']:.1f}M @ {row['ownership_pct']:.1f}%</div>
                <div style="font-family:IBM Plex Mono; font-size:0.7rem; color:#8890b8;">Current Val: ${row['current_valuation']:.0f}M</div>
                <div style="font-family:IBM Plex Mono; font-size:1rem; font-weight:600; color:{moic_color}; margin-top:4px;">{moic:.2f}x MOIC</div>
              </div>
            </div>""", unsafe_allow_html=True)

        # Portfolio charts
        st.markdown('<div class="section-label">Portfolio Analytics</div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)
        with ch1:
            fig = px.pie(port_df, values="invested_amount", names="company",
                title="Capital Allocation", color_discrete_sequence=["#c9a84c","#3ecfb2","#60a5fa","#a78bfa","#e05c5c","#e8c97a"])
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10), margin=dict(l=0,r=0,t=40,b=0), height=280)
            st.plotly_chart(fig, use_container_width=True)
        with ch2:
            port_df["moic_calc"] = port_df.apply(lambda r: (r["current_valuation"]*r["ownership_pct"]/100)/r["invested_amount"] if r["invested_amount"]>0 else 0, axis=1)
            colors = ["#3ecfb2" if m>=2 else ("#c9a84c" if m>=1 else "#e05c5c") for m in port_df["moic_calc"]]
            fig2 = go.Figure(go.Bar(x=port_df["company"], y=port_df["moic_calc"], marker_color=colors))
            fig2.add_hline(y=1, line_dash="dot", line_color="#4a5075")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
                title=dict(text="MOIC by Company", font=dict(color="#c9a84c",size=12)),
                margin=dict(l=10,r=10,t=40,b=10), height=280,
                yaxis=dict(gridcolor="#1e2130",title="MOIC"), xaxis=dict(gridcolor="#1e2130"))
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.markdown('<div class="card" style="text-align:center; padding:3rem;"><div style="font-family:IBM Plex Mono; color:#4a5075; font-size:0.8rem; letter-spacing:2px;">NO PORTFOLIO COMPANIES YET — ADD YOUR FIRST ABOVE</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 6 — COMPARABLE DEAL FINDER
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-label">Comparable Deal Finder</div>', unsafe_allow_html=True)

    cx1, cx2, cx3 = st.columns(3)
    with cx1:
        comp_company = st.text_input("Company or Market", placeholder="e.g. 'Databricks', 'AI data infrastructure'", key="comp_finder_co")
        comp_stage = st.selectbox("Stage", ["Any","Seed","Series A","Series B","Series C","Growth","PE Buyout"], key="comp_stage")
    with cx2:
        comp_sector = st.selectbox("Sector", ["Any","AI/ML","Fintech","Healthcare","SaaS","Consumer","Deeptech","Climate","Biotech"], key="comp_sector_f")
        comp_geo = st.selectbox("Geography", ["Global","North America","Europe","Asia-Pacific"], key="comp_geo")
    with cx3:
        comp_timeframe = st.selectbox("Deal Timeframe", ["Last 12 months","Last 2 years","Last 3 years"], key="comp_tf")
        comp_size = st.selectbox("Deal Size", ["Any","<$10M","$10M-$50M","$50M-$200M","$200M+"], key="comp_size")

    if st.button("▶  Find Comparable Deals", key="run_comps_finder") and comp_company:
        system = """You are a VC/PE research analyst. Search for real, recent comparable deals.
        Return ONLY valid JSON array, no markdown."""
        prompt = f"""Search for the most recent and relevant comparable deals/transactions for: {comp_company}
Stage: {comp_stage}, Sector: {comp_sector}, Geography: {comp_geo}, Timeframe: {comp_timeframe}, Size: {comp_size}

Return a JSON array of up to 10 deals with this structure:
[{{"company":"...","date":"...","round":"...","amount":"...","valuation":"...","investors":"...","multiple":"EV/Rev or EV/EBITDA if available","summary":"1-2 sentences about the deal and why it's comparable"}}]
Focus on real, verifiable deals with actual amounts. Include the most relevant comparables."""

        with st.spinner("Scanning deal databases…"):
            try:
                raw = stream_claude(prompt, system, max_tokens=2000, use_search=True, model="claude-sonnet-4-6")
                raw = raw.strip()
                if not raw:
                    st.error("No results returned. Try a more specific search term.")
                else:
                    if raw.startswith("```"):
                        raw = raw.split("```")[1]
                        if raw.startswith("json"):
                            raw = raw[4:]
                    start = raw.find("[")
                    end = raw.rfind("]") + 1
                    if start != -1 and end > start:
                        raw = raw[start:end]
                    try:
                        deals = json.loads(raw)
                        st.session_state["comp_deals"] = deals
                        st.session_state["comp_deals_query"] = comp_company
                    except Exception:
                        st.error("Could not parse results. Try again.")
            except Exception as e:
                st.error(f"Search failed: {e}")

    if "comp_deals" in st.session_state:
        deals = st.session_state["comp_deals"]
        st.markdown(f'<div class="section-label">Comparable Deals for: {st.session_state.get("comp_deals_query","")}</div>', unsafe_allow_html=True)

        amounts = []
        for deal in deals:
            amount_str = deal.get("amount","").replace("$","").replace("M","").replace("B","000").replace(",","")
            try: amounts.append(float(amount_str))
            except: amounts.append(0)

        if any(a>0 for a in amounts):
            avg_deal = sum(amounts)/len([a for a in amounts if a>0])
            c1,c2 = st.columns(2)
            with c1: st.markdown(f'<div class="metric-pill"><div class="label">Deals Found</div><div class="val">{len(deals)}</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-pill"><div class="label">Avg Deal Size</div><div class="val">${avg_deal:.0f}M</div></div>', unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        for deal in deals:
            st.markdown(f"""<div class="news-item">
              <div class="news-headline">{deal.get('company','')} — {deal.get('round','')} {deal.get('amount','')}</div>
              <div class="news-meta">
                <span class="news-tag tag-round">{deal.get('date','')}</span>
                {'<span class="news-tag tag-vc">Val: ' + deal.get('valuation','') + '</span>' if deal.get('valuation') else ''}
                {'<span class="news-tag tag-pe">Multiple: ' + deal.get('multiple','') + '</span>' if deal.get('multiple') else ''}
              </div>
              <div class="news-summary">{deal.get('summary','')}</div>
              {'<div class="news-meta" style="margin-top:6px;">Investors: ' + deal.get('investors','') + '</div>' if deal.get('investors') else ''}
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 7 — SCENARIO STRESS TESTER
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div class="section-label">Scenario Stress Tester — Bull / Base / Bear</div>', unsafe_allow_html=True)

    model_choice = st.selectbox("Model Type", ["DCF", "VC Method", "LBO"], key="scenario_model")
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    if model_choice == "DCF":
        s1, s2 = st.columns(2)
        with s1:
            sc_co = st.text_input("Company", "Portfolio Co.", key="sc_co")
            sc_base_rev = st.number_input("Base Revenue ($M)", value=50.0, step=5.0, key="sc_rev")
            sc_wacc = st.slider("WACC (%)", 5, 25, 12, key="sc_wacc")
            sc_tgr = st.slider("Terminal Growth Rate (%)", 1, 5, 3, key="sc_tgr")
        with s2:
            st.markdown("**Bull / Base / Bear Assumptions**")
            sh = st.columns(3)
            sh[0].markdown('<div style="font-family:IBM Plex Mono; font-size:0.65rem; color:#3ecfb2; letter-spacing:1px;">BULL</div>', unsafe_allow_html=True)
            sh[1].markdown('<div style="font-family:IBM Plex Mono; font-size:0.65rem; color:#c9a84c; letter-spacing:1px;">BASE</div>', unsafe_allow_html=True)
            sh[2].markdown('<div style="font-family:IBM Plex Mono; font-size:0.65rem; color:#e05c5c; letter-spacing:1px;">BEAR</div>', unsafe_allow_html=True)
            bull_g = sh[0].number_input("Rev Growth (%)", value=50.0, key="bull_g")
            base_g = sh[1].number_input("Rev Growth (%)", value=30.0, key="base_g")
            bear_g = sh[2].number_input("Rev Growth (%)", value=10.0, key="bear_g")
            bull_m = sh[0].number_input("EBITDA Margin (%)", value=30.0, key="bull_m")
            base_m = sh[1].number_input("EBITDA Margin (%)", value=20.0, key="base_m")
            bear_m = sh[2].number_input("EBITDA Margin (%)", value=5.0, key="bear_m")

        if st.button("▶  Run Scenario Analysis", key="run_scenarios"):
            def dcf_ev(base, growth, margin, wacc, tgr, years=7, capex=5, tax=25):
                rev = base; fcfs = []
                for _ in range(years):
                    rev *= (1+growth/100)
                    ebitda = rev*(margin/100)
                    nopat = ebitda*(1-tax/100)
                    fcf = nopat - rev*(capex/100)
                    fcfs.append(fcf)
                dfs = [(1/(1+wacc/100)**y) for y in range(1,years+1)]
                pv_fcfs = [f*d for f,d in zip(fcfs,dfs)]
                tv = fcfs[-1]*(1+tgr/100)/((wacc-tgr)/100)
                return sum(pv_fcfs)+tv*dfs[-1], [sc_base_rev*(1+growth/100)**y for y in range(1,years+1)]

            bull_ev, bull_revs = dcf_ev(sc_base_rev, bull_g, bull_m, sc_wacc, sc_tgr)
            base_ev, base_revs = dcf_ev(sc_base_rev, base_g, base_m, sc_wacc, sc_tgr)
            bear_ev, bear_revs = dcf_ev(sc_base_rev, bear_g, bear_m, sc_wacc, sc_tgr)

            st.session_state["scenarios"] = dict(
                bull_ev=bull_ev, base_ev=base_ev, bear_ev=bear_ev,
                bull_revs=bull_revs, base_revs=base_revs, bear_revs=bear_revs, co=sc_co
            )

        if "scenarios" in st.session_state:
            r = st.session_state["scenarios"]
            st.markdown(f'<div class="section-label">Scenario Results — {r["co"]}</div>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1: st.markdown(f'<div class="metric-pill"><div class="label positive">Bull EV</div><div class="val positive">${r["bull_ev"]:.1f}M</div></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="metric-pill"><div class="label" style="color:#c9a84c">Base EV</div><div class="val" style="color:#c9a84c">${r["base_ev"]:.1f}M</div></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="metric-pill"><div class="label negative">Bear EV</div><div class="val negative">${r["bear_ev"]:.1f}M</div></div>', unsafe_allow_html=True)

            yrs = [f"Yr {y}" for y in range(1,8)]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=yrs, y=r["bull_revs"], name="Bull", line=dict(color="#3ecfb2",width=2), fill='tonexty' if False else None))
            fig.add_trace(go.Scatter(x=yrs, y=r["base_revs"], name="Base", line=dict(color="#c9a84c",width=2,dash="dot")))
            fig.add_trace(go.Scatter(x=yrs, y=r["bear_revs"], name="Bear", line=dict(color="#e05c5c",width=2)))
            fig.add_trace(go.Scatter(x=yrs+yrs[::-1], y=r["bull_revs"]+r["bear_revs"][::-1],
                fill='toself', fillcolor='rgba(201,168,76,0.07)', line=dict(color='rgba(0,0,0,0)'), showlegend=False))
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10),
                legend=dict(bgcolor="rgba(0,0,0,0)"), margin=dict(l=10,r=10,t=30,b=10), height=300,
                yaxis=dict(gridcolor="#1e2130",title="Revenue ($M)"), xaxis=dict(gridcolor="#1e2130"),
                title=dict(text="Revenue Scenarios — 7 Year Projection", font=dict(color="#c9a84c",size=12)))
            st.plotly_chart(fig, use_container_width=True)

            # Tornado chart — sensitivity
            st.markdown('<div class="section-label">EV Sensitivity Range</div>', unsafe_allow_html=True)
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(name="Upside", x=[r["bull_ev"]-r["base_ev"]], y=["Enterprise Value"],
                orientation='h', marker_color="#3ecfb2", base=r["base_ev"]))
            fig2.add_trace(go.Bar(name="Downside", x=[r["bear_ev"]-r["base_ev"]], y=["Enterprise Value"],
                orientation='h', marker_color="#e05c5c", base=r["base_ev"]))
            fig2.add_vline(x=r["base_ev"], line_dash="dot", line_color="#c9a84c", annotation_text=f"Base: ${r['base_ev']:.0f}M")
            fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="IBM Plex Mono", color="#8890b8", size=10), barmode="overlay",
                margin=dict(l=10,r=10,t=20,b=10), height=160,
                xaxis=dict(gridcolor="#1e2130",title="Enterprise Value ($M)"), yaxis=dict(gridcolor="#1e2130"),
                legend=dict(bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig2, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 8 — VC / PE NEWS
# ══════════════════════════════════════════════════════════════════════════════
with tab8:
    st.markdown('<div class="section-label">Live VC / PE Intelligence Feed</div>', unsafe_allow_html=True)

    n1, n2, n3 = st.columns([2,2,1])
    with n1: news_focus = st.selectbox("Focus", ["All VC & PE News","Venture Capital","Private Equity","Exits & IPOs","Mega Rounds ($100M+)","Early Stage","AI & Tech","Biotech","Climate & Deeptech"], key="news_focus")
    with n2: news_region = st.selectbox("Region", ["Global","North America","Europe","Asia-Pacific","Emerging Markets"], key="news_region")
    with n3: n_stories = st.number_input("# Stories", 5, 20, 8, key="n_stories")

    if st.button("▶  Fetch Latest News", key="fetch_news"):
        system_news = """You are a financial journalist. Return ONLY valid JSON array (no markdown):
        [{"headline":"...","date":"...","category":"VC|PE|EXIT|ROUND|IPO","summary":"2-3 sentences","amount":"$XM or null","companies":"...","source":"..."}]"""
        prompt = f"""Search for {n_stories} most recent {news_focus} news from {news_region}. Focus on real deals, fundraises, exits. Return ONLY valid JSON array."""
        with st.spinner("Scanning financial news feeds…"):
            try:
                raw = stream_claude(prompt, system_news, max_tokens=3000, use_search=True)
                raw = raw.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"): raw = raw[4:]
                st.session_state["news_items"] = json.loads(raw)
            except Exception as e:
                st.error(f"Failed to fetch news: {e}")

    if "news_items" in st.session_state and st.session_state["news_items"]:
        for item in st.session_state["news_items"]:
            cat = item.get("category","VC").upper()
            tag_class = {"VC":"tag-vc","PE":"tag-pe","EXIT":"tag-exit","IPO":"tag-exit"}.get(cat,"tag-round")
            amount_html = f'<span class="news-tag tag-round">{item["amount"]}</span>' if item.get("amount") else ""
            st.markdown(f"""<div class="news-item">
              <div class="news-headline">{item.get('headline','')}</div>
              <div class="news-meta">
                <span class="news-tag {tag_class}">{cat}</span> {amount_html}
                {'<span class="news-tag" style="color:#8890b8;border-color:#4a5075">' + item.get('source','') + '</span>' if item.get('source') else ''}
                {'<span style="margin-left:8px">📅 ' + item.get('date','') + '</span>' if item.get('date') else ''}
              </div>
              <div class="news-summary">{item.get('summary','')}</div>
              {'<div class="news-meta" style="margin-top:6px;">🏢 ' + item.get('companies','') + '</div>' if item.get('companies') else ''}
            </div>""", unsafe_allow_html=True)
    elif "news_items" not in st.session_state:
        st.markdown('<div class="card" style="text-align:center;padding:3rem;"><div style="font-family:IBM Plex Mono;color:#4a5075;font-size:0.8rem;letter-spacing:2px;">CLICK "FETCH LATEST NEWS" TO LOAD THE INTELLIGENCE FEED</div></div>', unsafe_allow_html=True)
