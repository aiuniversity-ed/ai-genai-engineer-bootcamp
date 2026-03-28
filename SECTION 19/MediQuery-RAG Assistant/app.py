"""
app.py — MediQuery Streamlit UI.

Run: streamlit run app.py
"""

import os
import streamlit as st
from ingest_data import run_ingestion
from chain import ask

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MediQuery",
    page_icon="🩺",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { max-width: 900px; margin: 0 auto; }
    .stChatMessage { border-radius: 12px; }
    .source-card {
        background: #f0f7ff;
        border-left: 3px solid #2563eb;
        padding: 10px 14px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 0.85rem;
        color: #1e3a5f;
    }
    .badge {
        background: #dbeafe;
        color: #1d4ed8;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🩺 MediQuery")
    st.caption("Local RAG · Powered by llama3.2 + Ollama")
    st.divider()

    st.subheader("📂 Upload Documents")
    uploaded_files = st.file_uploader(
        "Upload medical PDFs",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        if st.button("📥 Ingest Documents", use_container_width=True, type="primary"):
            os.makedirs("./data", exist_ok=True)
            for f in uploaded_files:
                with open(f"./data/{f.name}", "wb") as out:
                    out.write(f.getbuffer())

            with st.spinner("Ingesting and embedding documents..."):
                try:
                    run_ingestion("./data")
                    st.success(f"✓ Ingested {len(uploaded_files)} file(s)!")
                    st.session_state["docs_ready"] = True
                except Exception as e:
                    st.error(f"Ingestion failed: {e}")

    st.divider()

    # Check if ChromaDB already exists
    db_exists = os.path.exists("./chroma_db")
    if db_exists:
        st.success("✓ Vector store loaded")
    else:
        st.warning("No documents ingested yet. Upload PDFs above.")

    st.divider()
    st.caption("⚙️ Settings")
    top_k = st.slider("Chunks to retrieve (k)", min_value=2, max_value=8, value=4)
    show_sources = st.toggle("Show source chunks", value=True)

    st.divider()
    if st.button("🗑️ Clear chat history"):
        st.session_state["messages"] = []
        st.rerun()

# ── Main area ──────────────────────────────────────────────────────────────────
st.title("🩺 MediQuery")
st.caption("Ask questions about your uploaded medical documents. All data stays local.")

# Init chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and show_sources and msg.get("sources"):
            with st.expander(f"📄 Sources ({len(msg['sources'])} chunks)"):
                for doc in msg["sources"]:
                    src = doc.metadata.get("source", "unknown").split("/")[-1]
                    page = doc.metadata.get("page", "?")
                    st.markdown(
                        f'<div class="source-card">'
                        f'<span class="badge">📄 {src} · page {page}</span><br><br>'
                        f'{doc.page_content[:400]}{"..." if len(doc.page_content) > 400 else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

# Chat input
if question := st.chat_input("Ask a question about your medical documents..."):
    if not os.path.exists("./chroma_db"):
        st.warning("Please upload and ingest documents first using the sidebar.")
        st.stop()

    # Show user message
    st.session_state["messages"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            try:
                result = ask(question, k=top_k)
                answer = result["answer"]
                sources = result["sources"]
            except Exception as e:
                answer = f"⚠️ Error: {e}\n\nMake sure Ollama is running: `ollama serve`"
                sources = []

        st.markdown(answer)

        if show_sources and sources:
            with st.expander(f"📄 Sources ({len(sources)} chunks)"):
                for doc in sources:
                    src = doc.metadata.get("source", "unknown").split("/")[-1]
                    page = doc.metadata.get("page", "?")
                    st.markdown(
                        f'<div class="source-card">'
                        f'<span class="badge">📄 {src} · page {page}</span><br><br>'
                        f'{doc.page_content[:400]}{"..." if len(doc.page_content) > 400 else ""}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

    # Save to history
    st.session_state["messages"].append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })