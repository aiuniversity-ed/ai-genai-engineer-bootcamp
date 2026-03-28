"""
app.py — Streamlit UI connected to agent.py

Run:  streamlit run app.py
"""

import time
import requests
import streamlit as st

from agent import Agent, EventKind, AgentEvent

# Page config
st.set_page_config(
    page_title="Ollama Agent",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --bg:          #08090c;
  --surface:     #0e1015;
  --panel:       #12141a;
  --border:      #1e2030;
  --accent:      #00e5ff;
  --accent2:     #ff4d6d;
  --accent3:     #aaff6e;
  --text:        #d8dce8;
  --muted:       #4a4f68;
  --radius:      10px;
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Mono', monospace !important;
  background: var(--bg) !important;
  color: var(--text) !important;
}

/* ── Layout ── */
.main .block-container {
  max-width: 900px !important;
  margin: auto !important;
  padding: 1.5rem 2rem 7rem !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

/* ── Header ── */
.agent-header {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.8rem;
  letter-spacing: 0.08em;
  background: linear-gradient(90deg, var(--accent), var(--accent2));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  line-height: 1;
  margin-bottom: .2rem;
}
.agent-sub {
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-bottom: 1.6rem;
}

/* ── Chat turn wrapper ── */
.turn {
  margin-bottom: 2rem;
}

/* ── User bubble ── */
.user-bubble {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-bottom: 1.2rem;
}
.user-text {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius) var(--radius) 4px var(--radius);
  padding: 12px 16px;
  font-size: 0.87rem;
  max-width: 72%;
  line-height: 1.65;
  white-space: pre-wrap;
}
.badge-user {
  font-family: 'Bebas Neue';
  font-size: 0.7rem;
  background: var(--border);
  color: var(--muted);
  padding: 2px 8px;
  border-radius: 20px;
  align-self: flex-end;
  white-space: nowrap;
}

/* ── Agent trace block ── */
.trace-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  margin-bottom: .8rem;
}
.trace-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 14px;
  background: var(--panel);
  border-bottom: 1px solid var(--border);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--muted);
}
.trace-header .dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.dot-thought  { background: #5555ff; }
.dot-tool     { background: var(--accent2); }
.dot-result   { background: var(--accent3); }
.dot-final    { background: var(--accent); }
.dot-error    { background: var(--accent2); }
.trace-body {
  padding: 10px 14px;
  font-size: 0.82rem;
  line-height: 1.65;
  white-space: pre-wrap;
  word-break: break-word;
}

/* ── Final answer ── */
.final-block {
  background: var(--panel);
  border: 1px solid var(--accent);
  border-radius: var(--radius);
  padding: 14px 18px;
  font-size: 0.88rem;
  line-height: 1.75;
  white-space: pre-wrap;
  box-shadow: 0 0 18px rgba(0, 229, 255, 0.06);
}

/* ── Stats pill ── */
.stats-row {
  display: flex; gap: 12px; flex-wrap: wrap;
  margin-top: .7rem;
  font-size: 0.65rem;
  color: var(--muted);
}
.stat-pill {
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2px 10px;
}
.stat-pill b { color: var(--accent); }

/* ── Input ── */
.stChatInput input, .stChatInput textarea {
  background: var(--panel) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius) !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.87rem !important;
}
.stChatInput input:focus, .stChatInput textarea:focus {
  border-color: var(--accent) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,.1) !important;
}

/* ── Sidebar widgets ── */
.stSelectbox label, .stSlider label, .stNumberInput label {
  color: var(--muted) !important;
  font-size: 0.75rem !important;
}
div[data-baseweb="select"] > div {
  background: var(--panel) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 8px !important;
}
.stButton > button {
  background: var(--panel) !important;
  color: var(--text) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.76rem !important;
  transition: all .15s;
}
.stButton > button:hover {
  border-color: var(--accent) !important;
  color: var(--accent) !important;
}
hr { border-color: var(--border) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius:3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── Spinner ── */
.blink-bar {
  display: inline-flex; gap:4px; align-items:center; margin-left:4px;
}
.blink-bar span {
  display:inline-block; width:4px; height:14px;
  background: var(--accent); border-radius:2px;
  animation: pulse .8s ease-in-out infinite;
}
.blink-bar span:nth-child(2){animation-delay:.15s;}
.blink-bar span:nth-child(3){animation-delay:.3s;}
@keyframes pulse{0%,100%{opacity:.2;transform:scaleY(.6)}50%{opacity:1;transform:scaleY(1)}}
</style>
""", unsafe_allow_html=True)


# Ollama model list helper
def get_ollama_models() -> list[str]:
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        pass
    return ["llama3.2", "mistral", "gemma3", "qwen2.5"]


# Session state
if "history"     not in st.session_state: st.session_state.history     = []
if "turns"       not in st.session_state: st.session_state.turns       = []
if "total_steps" not in st.session_state: st.session_state.total_steps = 0
if "total_time"  not in st.session_state: st.session_state.total_time  = 0.0


# Sidebar
with st.sidebar:
    st.markdown("### ◈ Agent Config")
    st.divider()

    models = get_ollama_models()
    model = st.selectbox("Ollama model", models, index=0)

    temperature = st.slider("Temperature", 0.0, 1.0, 0.6, 0.05)
    max_steps   = st.slider("Max steps",   2,   16,  8,   1)

    st.divider()
    st.markdown("**Tools enabled**")
    from agent import TOOLS
    for t in TOOLS:
        st.markdown(f"<span style='color:#00e5ff;font-size:.75rem'>◆ {t}</span>",
                    unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state.history     = []
            st.session_state.turns       = []
            st.session_state.total_steps = 0
            st.session_state.total_time  = 0.0
            st.rerun()
    with col2:
        status_color = "#aaff6e" if models and "llama" in models[0] else "#ff4d6d"
        st.markdown(
            f"<div style='font-size:.68rem;color:{status_color};padding:6px 0'>"
            f"● Ollama {'online' if models else 'offline'}</div>",
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        f"<div style='font-size:.72rem;color:#4a4f68'>"
        f"Turns: <b style='color:#00e5ff'>{len(st.session_state.turns)}</b><br>"
        f"Steps: <b style='color:#00e5ff'>{st.session_state.total_steps}</b><br>"
        f"Time:  <b style='color:#00e5ff'>{st.session_state.total_time:.1f}s</b>"
        f"</div>",
        unsafe_allow_html=True,
    )


# Header
st.markdown('<div class="agent-header">OLLAMA AGENT</div>', unsafe_allow_html=True)
st.markdown('<div class="agent-sub">ReAct · Tool-calling · Streaming · Structured output</div>',
            unsafe_allow_html=True)


# Render a saved turn
def render_turn(turn: dict):
    st.markdown(f"""
    <div class="user-bubble">
      <div class="badge-user">YOU</div>
      <div class="user-text">{turn['user']}</div>
    </div>
    """, unsafe_allow_html=True)

    for evt in turn["events"]:
        kind = evt["kind"]
        content = evt["content"]

        if kind == EventKind.FINAL:
            st.markdown(f'''
            <div class="final-block">{content}</div>''', unsafe_allow_html=True)

        elif kind == EventKind.ERROR:
            st.markdown(f'''
            <div class="trace-block">
              <div class="trace-header"><div class="dot dot-error"></div> Error</div>
              <div class="trace-body" style="color:#ff4d6d">{content}</div>
            </div>''', unsafe_allow_html=True)

    # Stats
    stats = turn.get("stats", {})
    if stats:
        st.markdown(f"""
        <div class="stats-row">
          <div class="stat-pill">steps <b>{stats.get('steps', '?')}</b></div>
          <div class="stat-pill">time <b>{stats.get('elapsed', '?')}s</b></div>
          <div class="stat-pill">model <b>{stats.get('model', '?')}</b></div>
        </div>""", unsafe_allow_html=True)


# Render history
for turn in st.session_state.turns:
    render_turn(turn)
    st.markdown("<hr>", unsafe_allow_html=True)


# Input & live streaming
if prompt := st.chat_input("Ask the agent anything…"):

    # Show user message immediately
    st.markdown(f"""
    <div class="user-bubble">
      <div class="badge-user">YOU</div>
      <div class="user-text">{prompt}</div>
    </div>
    """, unsafe_allow_html=True)

    agent = Agent(model=model, temperature=temperature, max_steps=max_steps)

    # Accumulators for structured display
    thought_buf  = ""
    final_buf    = ""
    saved_events = []   # for persisting to session state
    step_count   = 0

    # Live placeholder containers
    thought_ph  = st.empty()
    tool_ph     = st.empty()
    result_ph   = st.empty()
    final_ph    = st.empty()
    spinner_ph  = st.empty()

    spinner_ph.markdown(
        '<div style="font-size:.75rem;color:#4a4f68">◈ Agent thinking'
        '<span class="blink-bar"><span></span><span></span><span></span></span></div>',
        unsafe_allow_html=True,
    )

    t_start = time.time()

    for evt in agent.run(prompt, history=st.session_state.history):

        if evt.kind == EventKind.THOUGHT:
            # silent — not shown
            pass

        elif evt.kind == EventKind.TOOL_CALL:
            step_count += 1
            saved_events.append({"kind": EventKind.TOOL_CALL, "content": evt.content, "meta": evt.meta})

        elif evt.kind == EventKind.TOOL_RESULT:
            saved_events.append({"kind": EventKind.TOOL_RESULT, "content": evt.content, "meta": evt.meta})

        elif evt.kind == EventKind.FINAL:
            spinner_ph.empty()
            final_buf += evt.content
            final_ph.markdown(
                f'<div class="final-block">{final_buf}▌</div>',
                unsafe_allow_html=True,
            )

        elif evt.kind == EventKind.ERROR:
            spinner_ph.empty()
            st.markdown(f'''
            <div class="trace-block">
              <div class="trace-header"><div class="dot dot-error"></div> Error</div>
              <div class="trace-body" style="color:#ff4d6d">{evt.content}</div>
            </div>''', unsafe_allow_html=True)
            saved_events.append({"kind": EventKind.ERROR, "content": evt.content})

        elif evt.kind == EventKind.DONE:
            spinner_ph.empty()
            step_count = evt.meta.get("steps", step_count)

    # Final answer — remove streaming cursor
    if final_buf:
        final_ph.markdown(
            f'<div class="final-block">{final_buf}</div>',
            unsafe_allow_html=True,
        )
        saved_events.append({"kind": EventKind.FINAL, "content": final_buf})

    elapsed = round(time.time() - t_start, 2)

    # Stats pill
    st.markdown(f"""
    <div class="stats-row">
      <div class="stat-pill">steps <b>{step_count}</b></div>
      <div class="stat-pill">time <b>{elapsed}s</b></div>
      <div class="stat-pill">model <b>{model}</b></div>
    </div>""", unsafe_allow_html=True)

    # Persist turn
    st.session_state.turns.append({
        "user":   prompt,
        "events": saved_events,
        "stats":  {"steps": step_count, "elapsed": elapsed, "model": model},
    })

    # Update conversation history for next turn
    st.session_state.history.append({"role": "user",      "content": prompt})
    st.session_state.history.append({"role": "assistant", "content": final_buf or "(no final answer)"})

    # Global stats
    st.session_state.total_steps += step_count
    st.session_state.total_time  += elapsed
