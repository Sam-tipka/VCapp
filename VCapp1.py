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

LOGO_B64 = "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"


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

def stream_claude(prompt, system="", max_tokens=4000, use_search=False, model="claude-opus-4-5"):
    client = get_client()
    kwargs = dict(
        model=model,
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
                result = stream_claude(prompt, system, max_tokens=3000, use_search=True, model="claude-sonnet-4-6")
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
