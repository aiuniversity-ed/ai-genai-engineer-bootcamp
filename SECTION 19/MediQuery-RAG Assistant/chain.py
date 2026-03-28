"""
chain.py — Build the RAG chain: retriever + prompt + llama3.2 via Ollama.
"""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough   
from langchain_core.output_parsers import StrOutputParser  
from retriever import get_retriever

LLM_MODEL = "llama3"  # pull with: ollama pull llama3.2

# ── System prompt ──────────────────────────────────────────────────────────────
# Instructs the model to stay grounded in the retrieved context only.
SYSTEM_PROMPT = """You are MediQuery, a helpful medical information assistant.
Answer the user's question using ONLY the context provided below.
If the answer is not found in the context, say:
"I couldn't find relevant information in the uploaded documents."

Do NOT make up information. Do NOT use outside knowledge.
Always mention which document or section your answer comes from.

Context:
{context}
"""

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def format_docs(docs) -> str:
    """Format retrieved chunks into a single context string with source labels."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        formatted.append(
            f"[Source {i}: {source}, page {page}]\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


def build_rag_chain(k: int = 4):
    """
    Construct and return the full RAG chain.

    Chain flow:
        question → retriever → format_docs → prompt → LLM → string output
    """
    retriever = get_retriever(k=k)

    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=0.1,   # low temp = more factual, less hallucination
    )

    chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | PROMPT_TEMPLATE
        | llm
        | StrOutputParser()
    )
    return chain


def ask(question: str, k: int = 4) -> dict:
    """
    Ask a question and return both the answer and the source chunks.

    Returns:
        dict with keys: 'answer' (str), 'sources' (list of Documents)
    """
    retriever = get_retriever(k=k)
    chain = build_rag_chain(k=k)

    sources = retriever.invoke(question)
    answer = chain.invoke(question)

    return {
        "answer": answer,
        "sources": sources,
    }


if __name__ == "__main__":
    print("MediQuery RAG Chain — test mode\n")
    question = "What are the recommended treatments for hypertension?"
    print(f"Question: {question}\n")
    result = ask(question)
    print("Answer:\n", result["answer"])
    print("\nSources used:")
    for doc in result["sources"]:
        print(f"  - {doc.metadata.get('source')} (page {doc.metadata.get('page')})")