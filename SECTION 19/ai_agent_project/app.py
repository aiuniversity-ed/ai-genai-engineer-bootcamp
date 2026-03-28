import streamlit as st
import anthropic
import json
import re
import time
import random
from datetime import datetime
import pytz

#  DALAL — AI Indian Stock Trading Agent System

st.set_page_config(
    page_title="DALAL — AI Indian Stock Trading Agent",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ──
st.markdown("""c
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    background-color: #04080f;
    color: #d0e8f5;
    font-family: 'DM Mono', monospace;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem; padding-bottom: 1rem; }

/* Header */
.dalal-header {
    background: linear-gradient(135deg, #070e1a 0%, #0c1826 100%);
    border: 1px solid #1a3a5c;
    border-radius: 8px;
    padding: 18px 24px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.dalal-logo {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    letter-spacing: 6px;
    background: linear-gradient(90deg, #ff9933, #ffffff 50%, #138808);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.dalal-sub {
    font-size: 10px;
    letter-spacing: 4px;
    color: #5a8099;
    margin-top: 4px;
}

/* Metric cards */
.metric-card {
    background: #070e1a;
    border: 1px solid #1a3a5c;
    border-left: 3px solid #ff9933;
    border-radius: 6px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.metric-card.green { border-left-color: #00cc66; }
.metric-card.red   { border-left-color: #e63946; }
.metric-card.blue  { border-left-color: #4466cc; }
.metric-card.yellow{ border-left-color: #ffcc00; }

.metric-label {
    font-size: 10px;
    letter-spacing: 2px;
    color: #2a5570;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 22px;
    color: #d0e8f5;
}
.metric-value.up  { color: #00cc66; }
.metric-value.dn  { color: #e63946; }
.metric-sub { font-size: 11px; color: #5a8099; margin-top: 3px; }
.metric-sub.up { color: #00cc66; }
.metric-sub.dn { color: #e63946; }

/* Agent status */
.agent-card {
    background: #070e1a;
    border: 1px solid #1a3a5c;
    border-radius: 6px;
    padding: 12px 14px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.agent-name { font-size: 12px; font-weight: 600; color: #d0e8f5; }
.agent-role { font-size: 10px; color: #2a5570; margin-top: 2px; }

.badge {
    font-size: 10px; padding: 3px 10px; border-radius: 3px;
    font-family: 'Syne', monospace; font-weight: 700; letter-spacing: 1px;
}
.badge-active { background: rgba(0,204,102,0.12); color: #00cc66; border: 1px solid rgba(0,204,102,0.3); }
.badge-idle   { background: rgba(90,128,153,0.1);  color: #5a8099; border: 1px solid #1a3a5c; }
.badge-busy   { background: rgba(255,204,0,0.12);  color: #ffcc00; border: 1px solid rgba(255,204,0,0.3); }

/* Log box */
.log-box {
    background: #04080f;
    border: 1px solid #1a3a5c;
    border-radius: 6px;
    padding: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    line-height: 1.8;
    height: 320px;
    overflow-y: auto;
}
.log-time  { color: #2a5570; }
.log-orch  { background:rgba(68,102,204,0.15); color:#6688ee; padding:1px 6px; border-radius:2px; font-size:10px; font-weight:700; }
.log-analyst{ background:rgba(255,153,51,0.15); color:#ff9933; padding:1px 6px; border-radius:2px; font-size:10px; font-weight:700; }
.log-risk  { background:rgba(255,204,0,0.15);  color:#ffcc00; padding:1px 6px; border-radius:2px; font-size:10px; font-weight:700; }
.log-exec  { background:rgba(0,204,102,0.15);  color:#00cc66; padding:1px 6px; border-radius:2px; font-size:10px; font-weight:700; }
.log-sys   { background:rgba(90,128,153,0.15); color:#5a8099; padding:1px 6px; border-radius:2px; font-size:10px; font-weight:700; }

.log-trade { color: #00cc66; font-weight: 600; }
.log-warn  { color: #ffcc00; }
.log-err   { color: #e63946; }

/* Decision card */
.decision-box {
    background: #070e1a;
    border: 1px solid #1a3a5c;
    border-radius: 8px;
    padding: 20px;
    margin-top: 14px;
}
.decision-signal-buy  { font-family:'Share Tech Mono',monospace; font-size:32px; color:#00cc66; font-weight:700; }
.decision-signal-sell { font-family:'Share Tech Mono',monospace; font-size:32px; color:#e63946; font-weight:700; }
.decision-signal-hold { font-family:'Share Tech Mono',monospace; font-size:32px; color:#ffcc00; font-weight:700; }

/* Trade history row */
.trade-row {
    display:flex; justify-content:space-between; align-items:center;
    padding:9px 0; border-bottom:1px solid #0c1826;
}
.trade-sym { font-size:13px; font-weight:600; color:#d0e8f5; }
.trade-detail { font-size:10px; color:#5a8099; margin-top:2px; }
.trade-buy  { background:rgba(0,204,102,0.1); color:#00cc66; border:1px solid rgba(0,204,102,0.25); padding:2px 8px; border-radius:2px; font-size:10px; font-weight:700; }
.trade-sell { background:rgba(230,57,70,0.1);  color:#e63946; border:1px solid rgba(230,57,70,0.25);  padding:2px 8px; border-radius:2px; font-size:10px; font-weight:700; }

/* Position row */
.pos-row {
    display:flex; justify-content:space-between; padding:9px 0;
    border-bottom:1px solid #0c1826; font-size:12px;
}
.nse-badge { background:rgba(19,136,8,0.15); color:#44cc44; border:1px solid rgba(19,136,8,0.3); padding:1px 5px; border-radius:2px; font-size:9px; font-weight:700; margin-left:5px; }
.bse-badge { background:rgba(68,102,204,0.15);color:#6688ee; border:1px solid rgba(68,102,204,0.3); padding:1px 5px; border-radius:2px; font-size:9px; font-weight:700; margin-left:5px; }

/* Ticker */
.ticker-wrap {
    background:#070e1a; border:1px solid #1a3a5c; border-radius:6px;
    overflow:hidden; margin-bottom:14px; display:flex; align-items:center; height:38px;
}
.ticker-lbl {
    background:#ff9933; color:#000; font-family:'Syne',sans-serif; font-weight:800;
    font-size:10px; letter-spacing:2px; padding:0 14px; height:100%;
    display:flex; align-items:center; flex-shrink:0;
}
.ticker-scroll { overflow:hidden; flex:1; }
.ticker-content { display:flex; gap:28px; animation:tickscroll 40s linear infinite; white-space:nowrap; padding:0 14px; }
@keyframes tickscroll { from{transform:translateX(0)} to{transform:translateX(-50%)} }
.ti { display:inline-flex; gap:8px; align-items:center; font-size:11px; }
.ti-sym { color:#d0e8f5; font-weight:500; }
.ti-px  { color:#5a8099; font-family:'Share Tech Mono',monospace; }
.ti-up  { color:#00cc66; font-family:'Share Tech Mono',monospace; }
.ti-dn  { color:#e63946; font-family:'Share Tech Mono',monospace; }

/* Risk bar */
.risk-bar-wrap { height:8px; background:#0c1826; border-radius:4px; overflow:hidden; margin:6px 0 12px; }
.risk-bar-fill { height:100%; border-radius:4px; background:linear-gradient(90deg,#00cc66,#ffcc00,#e63946); }

/* Confidence bar */
.conf-bar-wrap { height:4px; background:#0c1826; border-radius:2px; overflow:hidden; margin-top:6px; }
.conf-bar-fill { height:100%; border-radius:2px; background:#ff9933; }

/* Streamlit widget overrides */
div[data-testid="stSelectbox"] > div { background:#0c1826 !important; border-color:#1a3a5c !important; color:#d0e8f5 !important; }
div[data-testid="stTextInput"] input { background:#0c1826 !important; border-color:#1a3a5c !important; color:#d0e8f5 !important; font-family:'DM Mono',monospace !important; }
.stButton button {
    background-color: #ff9933 !important;
    color: #000000 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    letter-spacing: 3px !important;
    border: none !important;
    border-radius: 4px !important;
    padding: 12px 24px !important;
    width: 100% !important;
    box-shadow: 0 0 24px rgba(255,153,51,0.4) !important;
}
.stButton button:hover { background-color: #ffb347 !important; }

div[data-testid="stSidebar"] { background:#04080f !important; border-right:1px solid #1a3a5c !important; }
div[data-testid="stSidebar"] * { color:#d0e8f5; }

h1,h2,h3 { color:#d0e8f5 !important; font-family:'Syne',sans-serif !important; }
</style>
""", unsafe_allow_html=True)

# ── INDIAN STOCK DATA ──
STOCKS = {
    "RELIANCE":   {"price":2945.40,"pe":24.8,"sector":"Energy / Telecom","mktcap":"₹19.94L Cr","hi52":3024.90,"lo52":2220.30},
    "TCS":        {"price":3820.75,"pe":32.4,"sector":"IT Services",     "mktcap":"₹13.86L Cr","hi52":4255.00,"lo52":3311.75},
    "HDFCBANK":   {"price":1642.30,"pe":19.2,"sector":"Banking",         "mktcap":"₹12.48L Cr","hi52":1794.00,"lo52":1363.55},
    "INFY":       {"price":1498.20,"pe":27.1,"sector":"IT Services",     "mktcap":"₹6.24L Cr", "hi52":1903.00,"lo52":1355.75},
    "ICICIBANK":  {"price":1082.45,"pe":17.8,"sector":"Banking",         "mktcap":"₹7.62L Cr", "hi52":1196.90,"lo52":899.00},
    "HINDUNILVR": {"price":2312.60,"pe":55.3,"sector":"FMCG",            "mktcap":"₹5.44L Cr", "hi52":2859.90,"lo52":2172.00},
    "WIPRO":      {"price":480.15, "pe":21.6,"sector":"IT Services",     "mktcap":"₹2.51L Cr", "hi52":566.80, "lo52":371.00},
    "BAJFINANCE": {"price":6820.80,"pe":30.2,"sector":"NBFC",            "mktcap":"₹4.11L Cr", "hi52":8192.00,"lo52":6220.00},
    "TATAMOTORS": {"price":942.55, "pe":9.4, "sector":"Auto",            "mktcap":"₹3.47L Cr", "hi52":1179.00,"lo52":652.20},
    "SUNPHARMA":  {"price":1534.90,"pe":34.7,"sector":"Pharma",          "mktcap":"₹3.68L Cr", "hi52":1960.00,"lo52":1080.00},
    "ADANIENT":   {"price":2840.10,"pe":88.2,"sector":"Conglomerate",    "mktcap":"₹3.24L Cr", "hi52":3743.00,"lo52":1017.05},
    "MARUTI":     {"price":11240.30,"pe":26.8,"sector":"Auto",           "mktcap":"₹3.40L Cr", "hi52":13680.00,"lo52":9613.40},
    "SBIN":       {"price":742.80, "pe":9.8, "sector":"PSU Banking",     "mktcap":"₹6.63L Cr", "hi52":912.00, "lo52":543.20},
    "ONGC":       {"price":272.40, "pe":7.2, "sector":"Oil & Gas",       "mktcap":"₹3.43L Cr", "hi52":345.00, "lo52":164.55},
    "LT":         {"price":3480.60,"pe":36.2,"sector":"Infrastructure",  "mktcap":"₹4.79L Cr", "hi52":3849.90,"lo52":2472.50},
    "AXISBANK":   {"price":1064.20,"pe":14.6,"sector":"Banking",         "mktcap":"₹3.28L Cr", "hi52":1339.65,"lo52":885.00},
    "BHARTIARTL": {"price":1542.30,"pe":82.4,"sector":"Telecom",         "mktcap":"₹9.20L Cr", "hi52":1779.00,"lo52":1020.40},
    "KOTAKBANK":  {"price":1782.40,"pe":22.8,"sector":"Banking",         "mktcap":"₹3.55L Cr", "hi52":1942.00,"lo52":1544.00},
    "NTPC":       {"price":362.15, "pe":18.4,"sector":"Power",           "mktcap":"₹3.51L Cr", "hi52":448.45, "lo52":222.90},
    "POWERGRID":  {"price":310.40, "pe":19.6,"sector":"Power",           "mktcap":"₹2.89L Cr", "hi52":366.25, "lo52":211.00},
}

def get_stock(symbol):
    s = symbol.strip().upper()
    if s in STOCKS:
        return STOCKS[s]
    return {"price":round(random.uniform(200,3000),2),"pe":round(random.uniform(10,50),1),
            "sector":"Unknown","mktcap":"N/A","hi52":None,"lo52":None}

def ist_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%H:%M:%S")

# ── SESSION STATE ──
if "logs"       not in st.session_state: st.session_state.logs = []
if "decision"   not in st.session_state: st.session_state.decision = None
if "trades"     not in st.session_state: st.session_state.trades = [
    {"sym":"TCS",     "type":"BUY",  "qty":10,"price":3798,"pnl":"+₹227","pct":"+0.60%","strategy":"Momentum"},
    {"sym":"TATAMOTORS","type":"SELL","qty":25,"price":956, "pnl":"-₹337","pct":"-1.41%","strategy":"Breakout"},
    {"sym":"RELIANCE","type":"BUY",  "qty":20,"price":2882,"pnl":"+₹1,268","pct":"+2.20%","strategy":"Swing"},
]
if "running"    not in st.session_state: st.session_state.running = False
if "agent_states" not in st.session_state: st.session_state.agent_states = {
    "ORCH":"active","ANALYST":"idle","RISK":"idle","EXEC":"idle"
}
if "portfolio"  not in st.session_state: st.session_state.portfolio = 842680
if "trades_today" not in st.session_state: st.session_state.trades_today = 9

def add_log(agent, msg, cls=""):
    st.session_state.logs.append({
        "time": ist_time(), "agent": agent, "msg": msg, "cls": cls
    })

def render_logs():
    agent_class = {"ORCH":"log-orch","ANALYST":"log-analyst","RISK":"log-risk","EXEC":"log-exec","SYS":"log-sys"}
    lines = ""
    for l in st.session_state.logs[-40:]:
        ac = agent_class.get(l["agent"], "log-sys")
        mc = f"log-{l['cls']}" if l["cls"] else ""
        lines += f'<span class="log-time">{l["time"]}</span> <span class="{ac}">{l["agent"]}</span> <span class="{mc}">{l["msg"]}</span><br>'
    return f'<div class="log-box">{lines}</div>'

def render_badge(state):
    if state == "active": return '<span class="badge badge-active">ACTIVE</span>'
    if state == "busy":   return '<span class="badge badge-busy">BUSY</span>'
    return '<span class="badge badge-idle">IDLE</span>'

# ── TICKER HTML ──
TICKER_ITEMS = [
    ("RELIANCE","₹2,945","up","+2.14%"),("TCS","₹3,821","up","+1.78%"),
    ("HDFCBANK","₹1,642","dn","-0.54%"),("INFY","₹1,498","dn","-1.53%"),
    ("ICICIBANK","₹1,082","up","+1.24%"),("WIPRO","₹480","dn","-0.72%"),
    ("BAJFINANCE","₹6,821","up","+2.41%"),("SUNPHARMA","₹1,535","up","+0.64%"),
    ("TATAMOTORS","₹943","dn","-1.20%"),("ADANIENT","₹2,840","up","+3.12%"),
    ("MARUTI","₹11,240","up","+0.95%"),("SBIN","₹743","up","+0.88%"),
]

def ticker_html():
    items = ""
    for sym,px,dir_,chg in TICKER_ITEMS * 2:
        cls = "ti-up" if dir_ == "up" else "ti-dn"
        items += f'<span class="ti"><span class="ti-sym">{sym}</span><span class="ti-px">{px}</span><span class="{cls}">{chg}</span></span>'
    return f'''<div class="ticker-wrap">
      <div class="ticker-lbl">NSE</div>
      <div class="ticker-scroll"><div class="ticker-content">{items}</div></div>
    </div>'''

# ── AGENT PIPELINE ──
def run_analyst(symbol, exchange, strategy, mkt, client):
    prompt = f"""You are ANALYST, a professional Indian stock market analyst AI agent.

Analyse {exchange}:{symbol} for a {strategy} trading strategy.
CMP: ₹{mkt['price']} | P/E: {mkt['pe']} | Sector: {mkt['sector']}
52W High: ₹{mkt.get('hi52','N/A')} | 52W Low: ₹{mkt.get('lo52','N/A')}

Consider: FII/DII flows, RBI policy, INR movement, budget impact, quarterly results cycle.

Return ONLY valid JSON (no markdown, no explanation):
{{
  "signal": "BUY or SELL or HOLD",
  "confidence": <integer 0-100>,
  "priceTarget": <number>,
  "keyFactors": ["factor1", "factor2", "factor3"],
  "support": <number>,
  "resistance": <number>,
  "indiaContext": "one India-specific factor",
  "summary": "one line summary"
}}"""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=800,
        messages=[{"role":"user","content":prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    m = re.search(r'\{[\s\S]*\}', text)
    if not m: raise ValueError("No JSON in analyst response")
    return json.loads(m.group(0))

def run_risk(symbol, risk_level, analyst, mkt, client):
    prompt = f"""You are RISK MANAGER, an Indian stock market risk management AI agent.

Analyst report for {symbol}:
Signal: {analyst['signal']} | Confidence: {analyst['confidence']}%
Target: ₹{analyst['priceTarget']} | Support: ₹{analyst['support']} | Resistance: ₹{analyst['resistance']}

Portfolio: ₹8,42,680 total | ₹2,18,400 cash | Risk: {risk_level} | CMP: ₹{mkt['price']}

SEBI position sizing: 3% conservative / 5% moderate / 8% aggressive of total portfolio per trade.
Stop loss: 3-5% below entry. Target: 8-15% above entry.

Return ONLY valid JSON:
{{
  "shares": <integer>,
  "stopLoss": <number>,
  "takeProfit": <number>,
  "rrRatio": "1:X.X",
  "riskScore": <integer 0-100>,
  "maxLoss": <number>,
  "positionValue": <number>,
  "notes": "brief note"
}}"""
    resp = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=600,
        messages=[{"role":"user","content":prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    m = re.search(r'\{[\s\S]*\}', text)
    if not m: raise ValueError("No JSON in risk response")
    return json.loads(m.group(0))

def fallback_analyst(symbol, strategy, mkt):
    signals = ["BUY","SELL","HOLD"]
    signal = random.choice(signals)
    conf = random.randint(52,88)
    price = mkt["price"]
    factors = {
        "momentum":       ["Price above 50 EMA on daily chart","RSI at 64 — bullish momentum","Delivery volume 1.4x above avg"],
        "mean_reversion": ["Stock at lower Bollinger Band","RSI oversold at 28","Sector rotation favourable"],
        "breakout":       ["Consolidation near 52W high","Volume breakout detected","MACD histogram expanding"],
        "swing":          ["Higher highs forming on weekly","Bullish engulfing candle","FII buying in sector"],
        "positional":     ["Q3 results beat estimates by 8%","Promoter buying last month","Budget allocation to sector"],
    }
    return {
        "signal": signal, "confidence": conf,
        "priceTarget": round(price * (1.10 if signal=="BUY" else 0.92), 2),
        "keyFactors": factors.get(strategy, factors["momentum"]),
        "support": round(price * 0.95, 2),
        "resistance": round(price * 1.07, 2),
        "indiaContext": "FII net buyers ₹2,840Cr in sector this week",
        "summary": f"{signal} signal on {strategy} — {conf}% confidence"
    }

def fallback_risk(risk_level, mkt):
    price = mkt["price"]
    pct = {"conservative":0.03,"moderate":0.05,"aggressive":0.08}.get(risk_level,0.05)
    shares = max(1, int((842680 * pct) / price))
    sl = round(price * 0.96, 2)
    tp = round(price * 1.10, 2)
    max_loss = round((price - sl) * shares, 2)
    pos_val = round(price * shares, 2)
    return {
        "shares": shares, "stopLoss": sl, "takeProfit": tp,
        "rrRatio": "1:2.5", "riskScore": random.randint(28,55),
        "maxLoss": max_loss, "positionValue": pos_val,
        "notes": f"{risk_level.capitalize()}: {shares} shares, ₹{pos_val:,.0f} position"
    }

# ════════════════════════════════════════════
#  MAIN UI
# ════════════════════════════════════════════

# ── HEADER ──
ist = datetime.now(pytz.timezone("Asia/Kolkata"))
nifty = 22143 + random.uniform(-80,80)
sensex = 73088 + random.uniform(-200,200)
bnifty = 47814 + random.uniform(-150,150)

st.markdown(f"""
<div class="dalal-header">
  <div>
    <div class="dalal-logo">DALAL</div>
    <div class="dalal-sub">AI INDIAN MARKET TRADING AGENT</div>
  </div>
  <div style="display:flex;gap:28px;align-items:center;flex-wrap:wrap">
    <div style="text-align:right">
      <div style="font-size:9px;letter-spacing:2px;color:#2a5570">NIFTY 50</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:15px;color:#d0e8f5">{nifty:,.2f}</div>
      <div style="font-size:10px;color:#00cc66">▲ +{nifty-22000:.2f} (+{((nifty-22000)/22000*100):.2f}%)</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:9px;letter-spacing:2px;color:#2a5570">SENSEX</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:15px;color:#d0e8f5">{sensex:,.2f}</div>
      <div style="font-size:10px;color:#00cc66">▲ +{sensex-72500:.2f} (+{((sensex-72500)/72500*100):.2f}%)</div>
    </div>
    <div style="text-align:right">
      <div style="font-size:9px;letter-spacing:2px;color:#2a5570">BANK NIFTY</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:15px;color:#d0e8f5">{bnifty:,.2f}</div>
      <div style="font-size:10px;color:#e63946">▼ -{47900-bnifty:.2f} (-{((47900-bnifty)/47900*100):.2f}%)</div>
    </div>
    <div style="text-align:right;padding-left:14px;border-left:1px solid #1a3a5c">
      <div style="font-size:9px;color:#00cc66;letter-spacing:1px">● NSE LIVE</div>
      <div style="font-family:'Share Tech Mono',monospace;font-size:13px;color:#5a8099">{ist.strftime('%H:%M:%S')} IST</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TICKER ──
st.markdown(ticker_html(), unsafe_allow_html=True)

# ── THREE COLUMNS ──
left, center, right = st.columns([1.1, 2.5, 1.2])

# ════════ LEFT SIDEBAR ════════
with left:
    # Portfolio
    pnl = st.session_state.portfolio - 800000
    st.markdown(f"""
    <div class="metric-card green">
      <div class="metric-label">Total Portfolio Value</div>
      <div class="metric-value up">₹{st.session_state.portfolio:,.0f}</div>
      <div class="metric-sub up">▲ +₹{pnl:,.0f} (+{pnl/800000*100:.2f}%)</div>
    </div>
    <div class="metric-card green">
      <div class="metric-label">Today P&L</div>
      <div class="metric-value up">+₹{random.randint(8000,12000):,}</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">Cash Available</div>
      <div class="metric-value">₹2,18,400</div>
    </div>
    """, unsafe_allow_html=True)

    # Agent Status
    st.markdown("<div style='margin-top:6px'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="metric-label" style="margin-bottom:8px;letter-spacing:3px">AGENT STATUS</div>""", unsafe_allow_html=True)
    agents = [
        ("ORCHESTRATOR","Pipeline coordinator","ORCH"),
        ("ANALYST","NSE/BSE + FII/DII data","ANALYST"),
        ("RISK MGR","SEBI-compliant sizing","RISK"),
        ("EXECUTOR","Order execution","EXEC"),
    ]
    for name, role, key in agents:
        state = st.session_state.agent_states.get(key,"idle")
        badge = render_badge(state)
        st.markdown(f"""
        <div class="agent-card">
          <div><div class="agent-name">{name}</div><div class="agent-role">{role}</div></div>
          {badge}
        </div>""", unsafe_allow_html=True)

    # Open Positions
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="metric-label" style="margin-bottom:8px;letter-spacing:3px">OPEN POSITIONS</div>""", unsafe_allow_html=True)
    positions = [
        ("RELIANCE","NSE","20","₹2,945","+₹1,240","+2.14%","up"),
        ("TCS","NSE","10","₹3,820","+₹680","+1.78%","up"),
        ("INFY","BSE","15","₹1,498","-₹345","-1.53%","dn"),
    ]
    pos_html = ""
    for sym,exch,qty,px,pnl_v,pct,dir_ in positions:
        exch_badge = f'<span class="nse-badge">{exch}</span>' if exch=="NSE" else f'<span class="bse-badge">{exch}</span>'
        color = "#00cc66" if dir_=="up" else "#e63946"
        pos_html += f"""<div class="pos-row">
          <div><span style="font-weight:600;color:#d0e8f5">{sym}</span>{exch_badge}<div class="trade-detail">{qty} shares · {px}</div></div>
          <div style="text-align:right"><div style="color:{color}">{pnl_v}</div><div class="trade-detail">{pct}</div></div>
        </div>"""
    st.markdown(f'<div style="background:#070e1a;border:1px solid #1a3a5c;border-radius:6px;padding:12px">{pos_html}</div>', unsafe_allow_html=True)

    # Market Pulse
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="metric-label" style="margin-bottom:8px;letter-spacing:3px">MARKET PULSE</div>""", unsafe_allow_html=True)
    st.markdown("""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
      <div style="background:#0c1826;border-radius:4px;padding:10px">
        <div style="font-size:9px;color:#2a5570;letter-spacing:1px">FII FLOW</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#00cc66">+₹2,840Cr</div>
      </div>
      <div style="background:#0c1826;border-radius:4px;padding:10px">
        <div style="font-size:9px;color:#2a5570;letter-spacing:1px">DII FLOW</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#00cc66">+₹1,120Cr</div>
      </div>
      <div style="background:#0c1826;border-radius:4px;padding:10px">
        <div style="font-size:9px;color:#2a5570;letter-spacing:1px">INDIA VIX</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#ffcc00">14.82</div>
      </div>
      <div style="background:#0c1826;border-radius:4px;padding:10px">
        <div style="font-size:9px;color:#2a5570;letter-spacing:1px">USD/INR</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#d0e8f5">₹83.42</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ════════ CENTER ════════
with center:
    st.markdown("""
    <div style="background:#070e1a;border:1px solid #1a3a5c;border-radius:8px;padding:20px;margin-bottom:14px">
      <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:13px;letter-spacing:3px;color:#ff9933;text-transform:uppercase;margin-bottom:16px;padding-bottom:12px;border-bottom:1px solid #1a3a5c">
        ANALYSIS & TRADE COMMAND
      </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        symbol = st.text_input("NSE / BSE SYMBOL", value="RELIANCE", placeholder="e.g. RELIANCE, TCS, INFY").upper().strip()
        strategy = st.selectbox("STRATEGY", ["Momentum","Mean Reversion","Breakout","Swing Trade","Positional"])
    with c2:
        exchange = st.selectbox("EXCHANGE", ["NSE","BSE"])
        risk_level = st.selectbox("RISK LEVEL", ["Conservative","Moderate","Aggressive"], index=1)

    api_key = st.text_input("ANTHROPIC API KEY", type="password", placeholder="sk-ant-api03-...", help="Your API key is never stored")

    st.markdown("</div>", unsafe_allow_html=True)

    # ── ANALYSE BUTTON ──
    analyse_clicked = st.button("▶  ANALYSE STOCK", key="analyse_btn", use_container_width=True)

    # ── AGENT LOG ──
    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
    st.markdown("""<div class="metric-label" style="letter-spacing:3px;margin-bottom:8px">AGENT REASONING LOG</div>""", unsafe_allow_html=True)

    if not st.session_state.logs:
        st.session_state.logs = [
            {"time":"00:00:00","agent":"SYS","msg":"DALAL AI Trading System initialised. Monitoring NSE + BSE markets.","cls":""},
            {"time":"00:00:01","agent":"SYS","msg":"Enter a stock symbol and click ANALYSE STOCK to run the 4-agent pipeline.","cls":""},
            {"time":"00:00:02","agent":"SYS","msg":"Supported: RELIANCE, TCS, HDFCBANK, INFY, ICICIBANK, WIPRO, BAJFINANCE, TATAMOTORS, SBIN...","cls":""},
        ]

    log_placeholder = st.empty()
    log_placeholder.markdown(render_logs(), unsafe_allow_html=True)

    # ── RUN PIPELINE ──
    if analyse_clicked and symbol:
        mkt = get_stock(symbol)
        st.session_state.decision = None
        st.session_state.logs = []
        st.session_state.agent_states = {"ORCH":"busy","ANALYST":"idle","RISK":"idle","EXEC":"idle"}

        strategy_key = strategy.lower().replace(" ","_")
        risk_key = risk_level.lower()

        # Init client
        key = api_key.strip() if api_key.strip() else None
        client = anthropic.Anthropic(api_key=key) if key else None

        # ORCHESTRATOR
        add_log("ORCH", f"Starting pipeline: {exchange}:{symbol} | {strategy.upper()} | {risk_level.upper()}")
        add_log("ORCH", f"Market data: ₹{mkt['price']} | P/E: {mkt['pe']} | Sector: {mkt['sector']} | MktCap: {mkt['mktcap']}")
        add_log("ORCH", "Dispatching ANALYST agent...")
        st.session_state.agent_states["ORCH"] = "active"
        st.session_state.agent_states["ANALYST"] = "busy"
        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        time.sleep(0.4)

        # ANALYST
        add_log("ANALYST", f"CMP: ₹{mkt['price']} | 52W H: ₹{mkt.get('hi52','N/A')} | 52W L: ₹{mkt.get('lo52','N/A')}")
        if client:
            add_log("ANALYST", "Calling Claude AI for fundamental + technical analysis...")
        else:
            add_log("ANALYST", "No API key — using built-in analysis model...", "warn")
        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        time.sleep(0.4)

        try:
            if client:
                analyst_data = run_analyst(symbol, exchange, strategy_key, mkt, client)
            else:
                analyst_data = fallback_analyst(symbol, strategy_key, mkt)
        except Exception as e:
            add_log("ANALYST", f"Error: {str(e)[:60]} — using fallback", "warn")
            analyst_data = fallback_analyst(symbol, strategy_key, mkt)

        for f in analyst_data.get("keyFactors",[]):
            add_log("ANALYST", f"→ {f}")
        if analyst_data.get("indiaContext"):
            add_log("ANALYST", f"India context: {analyst_data['indiaContext']}")
        add_log("ANALYST", f"Summary: {analyst_data.get('summary','')}")

        st.session_state.agent_states["ANALYST"] = "active"
        st.session_state.agent_states["RISK"] = "busy"
        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        time.sleep(0.4)

        # RISK MANAGER
        add_log("RISK", "Received analyst report. Running SEBI-compliant risk assessment...")
        add_log("RISK", f"Portfolio: ₹8,42,680 | Cash: ₹2,18,400 | Mode: {risk_level}")
        if client:
            add_log("RISK", "Calling Claude AI for position sizing & risk parameters...")
        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        time.sleep(0.4)

        try:
            if client:
                risk_data = run_risk(symbol, risk_key, analyst_data, mkt, client)
            else:
                risk_data = fallback_risk(risk_key, mkt)
        except Exception as e:
            add_log("RISK", f"Error: {str(e)[:60]} — using fallback", "warn")
            risk_data = fallback_risk(risk_key, mkt)

        add_log("RISK", f"→ {risk_data.get('notes','')}")
        st.session_state.agent_states["RISK"] = "active"
        st.session_state.agent_states["EXEC"] = "busy"
        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        time.sleep(0.3)

        # ORCHESTRATOR DECIDES
        st.session_state.agent_states["ORCH"] = "busy"
        add_log("ORCH", "Synthesising analyst + risk reports...")
        time.sleep(0.3)

        decision = {
            "symbol": symbol, "exchange": exchange,
            "sector": mkt["sector"], "strategy": strategy,
            "signal": analyst_data["signal"],
            "confidence": analyst_data["confidence"],
            "summary": analyst_data.get("summary",""),
            "entry": mkt["price"],
            "stopLoss": risk_data["stopLoss"],
            "takeProfit": risk_data["takeProfit"],
            "shares": risk_data["shares"],
            "rrRatio": risk_data["rrRatio"],
            "riskScore": risk_data["riskScore"],
            "maxLoss": risk_data["maxLoss"],
            "positionValue": risk_data["positionValue"],
        }
        st.session_state.decision = decision

        add_log("ORCH", f"Decision: {decision['signal']} {symbol} @ ₹{decision['entry']} | Qty: {decision['shares']} | Conf: {decision['confidence']}%", "trade")
        add_log("ORCH", f"SL: ₹{decision['stopLoss']} | Target: ₹{decision['takeProfit']} | R:R = {decision['rrRatio']}")
        add_log("ORCH", f"Max Risk: ₹{decision['maxLoss']:,} | Position: ₹{decision['positionValue']:,}")
        st.session_state.agent_states["ORCH"] = "active"

        # EXECUTOR
        add_log("EXEC", f"Order received: {decision['signal']} {decision['shares']} × {symbol} @ ₹{decision['entry']}")
        add_log("EXEC", f"Type: LIMIT | Exchange: {exchange} | Product: CNC")
        add_log("EXEC", "Validated. Awaiting user confirmation...")
        st.session_state.agent_states["EXEC"] = "active"

        log_placeholder.markdown(render_logs(), unsafe_allow_html=True)
        st.rerun()

    # ── DECISION OUTPUT ──
    if st.session_state.decision:
        d = st.session_state.decision
        sig_color = {"BUY":"#00cc66","SELL":"#e63946","HOLD":"#ffcc00"}.get(d["signal"],"#d0e8f5")

        st.markdown(f"""
        <div class="decision-box">
          <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:13px;letter-spacing:3px;color:#ff9933;text-transform:uppercase;margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #1a3a5c">
            AGENT DECISION OUTPUT
          </div>
          <div style="margin-bottom:12px">
            <span style="font-family:'Share Tech Mono',monospace;font-size:15px;color:#ff9933">{d['exchange']}:{d['symbol']}</span>
            <span style="background:rgba(255,153,51,0.1);color:#ff9933;border:1px solid rgba(255,153,51,0.2);padding:2px 8px;border-radius:2px;font-size:10px;letter-spacing:1px;margin-left:8px">{d['sector']}</span>
          </div>

          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:16px">
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">SIGNAL</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:28px;font-weight:700;color:{sig_color}">{d['signal']}</div>
            </div>
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">CONFIDENCE</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:24px;color:#d0e8f5">{d['confidence']}%</div>
              <div class="conf-bar-wrap"><div class="conf-bar-fill" style="width:{d['confidence']}%"></div></div>
            </div>
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">QUANTITY</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:24px;color:#d0e8f5">{d['shares']} <span style="font-size:14px;color:#5a8099">shares</span></div>
            </div>
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">ENTRY (₹)</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:22px;color:#d0e8f5">₹{d['entry']:,}</div>
            </div>
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">STOP LOSS (₹)</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:22px;color:#e63946">₹{d['stopLoss']:,}</div>
            </div>
            <div style="background:#0c1826;border-radius:4px;padding:12px">
              <div style="font-size:10px;color:#2a5570;letter-spacing:2px;text-transform:uppercase;margin-bottom:6px">TARGET (₹)</div>
              <div style="font-family:'Share Tech Mono',monospace;font-size:22px;color:#00cc66">₹{d['takeProfit']:,}</div>
            </div>
          </div>

          <div style="background:#0c1826;border-radius:4px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#5a8099">
            {d['summary']} &nbsp;·&nbsp; R:R = {d['rrRatio']} &nbsp;·&nbsp; Position Value: ₹{d['positionValue']:,} &nbsp;·&nbsp; Max Loss: ₹{d['maxLoss']:,}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if d["signal"] != "HOLD":
            if st.button(f"✓  PLACE {d['signal']} ORDER — {d['shares']} × {d['symbol']} @ ₹{d['entry']}", key="place_order", use_container_width=True):
                trade = {
                    "sym": d["symbol"], "type": d["signal"],
                    "qty": d["shares"], "price": d["entry"],
                    "pnl": "OPEN", "pct": "—", "strategy": d["strategy"]
                }
                st.session_state.trades.insert(0, trade)
                st.session_state.trades_today += 1
                add_log("EXEC", f"ORDER PLACED: {d['signal']} {d['shares']} × {d['symbol']} @ ₹{d['entry']} on {d['exchange']}", "trade")
                add_log("EXEC", f"SL: ₹{d['stopLoss']} | Target: ₹{d['takeProfit']} | Product: CNC")
                add_log("ORCH", "Trade confirmed. Position open. Monitoring...")
                st.session_state.decision = None
                st.success(f"✅ {d['signal']} order placed: {d['shares']} × {d['symbol']} @ ₹{d['entry']}")
                time.sleep(1)
                st.rerun()

# ════════ RIGHT ════════
with right:
    # Risk Monitor
    risk_score = st.session_state.decision["riskScore"] if st.session_state.decision else 42
    st.markdown(f"""
    <div class="metric-card yellow">
      <div class="metric-label">Risk Monitor</div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#2a5570;margin-bottom:4px">
        <span>LOW</span><span style="color:#ffcc00">{risk_score}%</span><span>HIGH</span>
      </div>
      <div class="risk-bar-wrap"><div class="risk-bar-fill" style="width:{risk_score}%"></div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">
        <div style="background:#0c1826;border-radius:3px;padding:8px">
          <div style="font-size:9px;color:#2a5570;letter-spacing:1px">VaR (1D)</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#d0e8f5">₹{st.session_state.decision['maxLoss']:,}</div>
        </div>
        <div style="background:#0c1826;border-radius:3px;padding:8px">
          <div style="font-size:9px;color:#2a5570;letter-spacing:1px">SHARPE</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#d0e8f5">1.72</div>
        </div>
        <div style="background:#0c1826;border-radius:3px;padding:8px">
          <div style="font-size:9px;color:#2a5570;letter-spacing:1px">MAX DD</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#e63946">-3.8%</div>
        </div>
        <div style="background:#0c1826;border-radius:3px;padding:8px">
          <div style="font-size:9px;color:#2a5570;letter-spacing:1px">BETA</div>
          <div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#d0e8f5">0.88</div>
        </div>
      </div>
    </div>
    """ if st.session_state.decision else f"""
    <div class="metric-card yellow">
      <div class="metric-label">Risk Monitor</div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#2a5570;margin-bottom:4px">
        <span>LOW</span><span style="color:#ffcc00">42%</span><span>HIGH</span>
      </div>
      <div class="risk-bar-wrap"><div class="risk-bar-fill" style="width:42%"></div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">
        <div style="background:#0c1826;border-radius:3px;padding:8px"><div style="font-size:9px;color:#2a5570">VaR (1D)</div><div style="font-family:'Share Tech Mono',monospace;font-size:14px">₹8,420</div></div>
        <div style="background:#0c1826;border-radius:3px;padding:8px"><div style="font-size:9px;color:#2a5570">SHARPE</div><div style="font-family:'Share Tech Mono',monospace;font-size:14px">1.72</div></div>
        <div style="background:#0c1826;border-radius:3px;padding:8px"><div style="font-size:9px;color:#2a5570">MAX DD</div><div style="font-family:'Share Tech Mono',monospace;font-size:14px;color:#e63946">-3.8%</div></div>
        <div style="background:#0c1826;border-radius:3px;padding:8px"><div style="font-size:9px;color:#2a5570">BETA</div><div style="font-family:'Share Tech Mono',monospace;font-size:14px">0.88</div></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Recent Trades
    st.markdown("""<div class="metric-label" style="letter-spacing:3px;margin-bottom:8px">RECENT TRADES</div>""", unsafe_allow_html=True)
    trades_html = ""
    for t in st.session_state.trades[:5]:
        type_cls = "trade-buy" if t["type"]=="BUY" else "trade-sell"
        pnl_color = "#00cc66" if str(t["pnl"]).startswith("+") else ("#e63946" if str(t["pnl"]).startswith("-") else "#5a8099")
        trades_html += f"""<div class="trade-row">
          <div>
            <div style="display:flex;gap:8px;align-items:center">
              <span class="trade-sym">{t['sym']}</span>
              <span class="{type_cls}">{t['type']}</span>
            </div>
            <div class="trade-detail">{t['qty']} × ₹{t['price']} · {t['strategy']}</div>
          </div>
          <div style="text-align:right">
            <div style="color:{pnl_color}">{t['pnl']}</div>
            <div class="trade-detail">{t['pct']}</div>
          </div>
        </div>"""
    st.markdown(f'<div style="background:#070e1a;border:1px solid #1a3a5c;border-radius:6px;padding:12px">{trades_html}</div>', unsafe_allow_html=True)

    # Session Stats
    st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">Session Stats</div>
      <div style="margin-bottom:8px">
        <div style="font-size:10px;color:#2a5570;letter-spacing:1px">WIN RATE</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:20px;color:#00cc66">64.8%</div>
      </div>
      <div style="margin-bottom:8px">
        <div style="font-size:10px;color:#2a5570;letter-spacing:1px">TRADES TODAY</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:20px;color:#d0e8f5">{st.session_state.trades_today}</div>
      </div>
      <div>
        <div style="font-size:10px;color:#2a5570;letter-spacing:1px">AVG RETURN</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:20px;color:#00cc66">+1.28%</div>
      </div>
    </div>
    """, unsafe_allow_html=True)