
# Run: streamlit run streamlit_app.py

import time
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

# ── Page Config (always FIRST) 
st.set_page_config(
    page_title="Streamlit Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SIDEBAR
st.sidebar.title("⚙️ Settings")
st.sidebar.slider("Top-p", 0.0, 1.0, 0.9, 0.01)
st.sidebar.selectbox("Output Language", ["English", "Hindi", "Kannada", "French"])
st.sidebar.number_input("Seed", value=42)

# PART 1 — HOME
st.title("🤖 Streamlit Demo")
st.markdown("""
This single file covers all Streamlit basics:
- ✅ Text Elements & Layout
- ✅ Input Widgets
- ✅ Displaying Output (tables, charts, code)
- ✅ Session State & Chat History
- ✅ Mini Project: Sentiment Analyzer
""")
st.divider()

# PART 2 — TEXT ELEMENTS & LAYOUT
st.header("📝 Part 2: Text Elements & Layout")

st.subheader("2.1 Text Elements")
st.write("st.write() renders text, dicts, DataFrames, charts…")
st.markdown("**Markdown**: _italics_, `code`, [links](https://streamlit.io)")
st.info("ℹ️ st.info()")
st.success("✅ st.success()")
st.warning("⚠️ st.warning()")
st.error("❌ st.error()")

st.subheader("2.2 Columns & Metrics")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Accuracy", "94.2%", "+1.3%")
with col2:
    st.metric("F1 Score", "0.91", "-0.02")
with col3:
    st.metric("Latency", "120 ms", "−15 ms")

st.subheader("2.3 Tabs")
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Data", "⚙️ Settings"])
with tab1:
    st.write("Content for Tab 1")
with tab2:
    st.write("Content for Tab 2")
with tab3:
    st.write("Content for Tab 3")

with st.expander("Click to expand — bonus content"):
    st.write("Hidden content revealed!")

st.divider()

# PART 3 — INPUT WIDGETS
st.header("🎛️ Part 3: Input Widgets")

st.subheader("3.1 Text Inputs")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Your name", placeholder="e.g. Priya")
with col2:
    query = st.text_area("Ask anything", placeholder="Type your question here…", height=120)

st.subheader("3.2 Numeric Inputs")
col1, col2 = st.columns(2)
with col1:
    temperature = st.slider("LLM Temperature", 0.0, 2.0, 0.7, 0.05,
                            help="Higher = creative, Lower = focused")
with col2:
    max_tokens = st.number_input("Max Tokens", min_value=50, max_value=4096, value=512, step=50)

st.subheader("3.3 Selection Widgets")
col1, col2 = st.columns(2)
with col1:
    model_choice = st.selectbox("Choose Model",
                                 ["gpt-4o", "gpt-3.5-turbo", "claude-3-sonnet", "gemini-pro"])
    features = st.multiselect("Enable Features",
                               ["Streaming", "Web Search", "Memory", "Function Calling"],
                               default=["Streaming"])
with col2:
    mode = st.radio("Response Mode", ["Concise", "Detailed", "Bullet Points"], horizontal=True)
    dark_mode = st.toggle("Dark Mode")
    show_sources = st.checkbox("Show sources", value=True)

st.subheader("3.4 File Uploader")
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "txt", "csv"])
if uploaded_file is not None:
    st.success(f"Uploaded: **{uploaded_file.name}** ({uploaded_file.size} bytes)")

st.subheader("3.5 Button")
if st.button("🚀 Run Analysis", type="primary"):
    st.write(f"Running: model=`{model_choice}`, temp=`{temperature}`, tokens=`{max_tokens}`")

st.divider()

# PART 4 — DISPLAYING OUTPUT
st.header("📊 Part 4: Displaying Output")

sample_data = pd.DataFrame({
    "Model":      ["GPT-4o", "Claude 3 Sonnet", "Gemini Pro", "Llama 3 70B"],
    "Accuracy":   [94.2, 93.8, 92.1, 90.5],
    "Latency ms": [210, 185, 230, 310],
    "Cost $/1M":  [5.00, 3.00, 0.35, 0.00],
})

st.subheader("4.1 DataFrame")
st.dataframe(sample_data, use_container_width=True)

st.subheader("4.2 Native Charts")
chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["Precision", "Recall", "F1"])
st.line_chart(chart_data)
st.bar_chart(sample_data.set_index("Model")["Accuracy"])

st.subheader("4.3 Matplotlib")
fig, ax = plt.subplots()
ax.barh(sample_data["Model"], sample_data["Accuracy"],
        color=["#4C9BE8", "#E8834C", "#4CE87A", "#E84C4C"])
ax.set_xlabel("Accuracy (%)")
ax.set_title("Model Comparison")
st.pyplot(fig)

st.subheader("4.4 Plotly — Interactive")
fig2 = px.scatter(
    sample_data, x="Latency ms", y="Accuracy",
    size="Cost $/1M", color="Model",
    title="Accuracy vs Latency (bubble size = cost)"
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("4.5 Code & JSON")
st.code("""
def classify_sentiment(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Sentiment of: {text}"}]
    )
    return response.choices[0].message.content
""", language="python")

st.json({"model": model_choice, "temperature": temperature, "max_tokens": max_tokens})

st.subheader("4.6 Progress & Spinner")
if st.button("Simulate Long Task"):
    bar = st.progress(0, text="Processing…")
    for i in range(100):
        time.sleep(0.02)
        bar.progress(i + 1, text=f"Processing… {i+1}%")
    st.success("Done!")

st.divider()

# PART 5 — SESSION STATE
st.header("🔁 Part 5: Session State")

st.subheader("5.1 Counter")
if "counter" not in st.session_state:
    st.session_state.counter = 0

col_a, col_b, col_c = st.columns(3)
if col_a.button("➕ Increment"):
    st.session_state.counter += 1
if col_b.button("➖ Decrement"):
    st.session_state.counter -= 1
if col_c.button("🔄 Reset"):
    st.session_state.counter = 0
st.metric("Counter Value", st.session_state.counter)

st.subheader("5.2 Persistent Chat History")
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if user_input := st.chat_input("Type a message…"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    reply = f"Echo: {user_input}"
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

if st.button("🗑️ Clear Chat"):
    st.session_state.messages = []
    st.rerun()

st.subheader("5.3 Forms")
with st.form("user_profile_form"):
    st.write("**User Profile**")
    fname  = st.text_input("First Name")
    lname  = st.text_input("Last Name")
    age    = st.number_input("Age", 18, 100)
    submit = st.form_submit_button("Save Profile")
if submit:
    st.success(f"Saved: {fname} {lname}, Age {age}")

st.divider()

# PART 6 — MINI PROJECT: SENTIMENT ANALYZER
st.header("🔍 Part 6: Mini Project — Sentiment Analyzer")
st.caption("Live-coding exercise — replace mock_sentiment() with a real LLM call in Part 2")

def mock_sentiment(text: str) -> dict:
    """Mock function — replace with real OpenAI / HuggingFace call."""
    label = random.choice(["POSITIVE", "NEGATIVE", "NEUTRAL"])
    score = round(random.uniform(0.60, 0.99), 2)
    emoji = {"POSITIVE": "😊", "NEGATIVE": "😠", "NEUTRAL": "😐"}[label]
    return {"label": label, "score": score, "emoji": emoji}

user_text = st.text_area("Enter text to analyse:", height=120,
                          placeholder="e.g. 'I love this product!'")

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("Analyse Sentiment", type="primary", disabled=not user_text.strip()):
    with st.spinner("Analysing…"):
        time.sleep(0.5)
        result = mock_sentiment(user_text)

    color = {"POSITIVE": "green", "NEGATIVE": "red", "NEUTRAL": "orange"}[result["label"]]
    st.markdown(
        f"**Result:** :{color}[{result['emoji']} {result['label']}]  "
        f"— Confidence: `{result['score']:.0%}`"
    )
    st.session_state.history.append({
        "Text":       user_text[:60] + ("…" if len(user_text) > 60 else ""),
        "Sentiment":  result["label"],
        "Confidence": f"{result['score']:.0%}",
    })

if st.session_state.history:
    st.subheader("📋 Analysis History")
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

st.divider()

# CHEAT SHEET
st.header("📋 Streamlit Cheat Sheet")
cheatsheet = pd.DataFrame({
    "Category": ["Text","Text","Text","Input","Input","Input","Input","Input",
                 "Output","Output","Output","Layout","Layout","State","Misc"],
    "Function":  ["st.title()","st.markdown()","st.write()","st.text_input()",
                  "st.slider()","st.selectbox()","st.file_uploader()","st.button()",
                  "st.dataframe()","st.line_chart()","st.plotly_chart()",
                  "st.columns()","st.tabs()","st.session_state","st.spinner()"],
    "Purpose":   ["Page title","Markdown text","Universal output","Single-line text",
                  "Numeric slider","Dropdown select","File upload","Trigger action",
                  "Interactive table","Quick line chart","Interactive Plotly figure",
                  "Side-by-side layout","Tabbed layout","Persist values across reruns",
                  "Loading spinner"],
})
st.dataframe(cheatsheet, use_container_width=True, hide_index=True)
st.caption("streamlit_app.py")
