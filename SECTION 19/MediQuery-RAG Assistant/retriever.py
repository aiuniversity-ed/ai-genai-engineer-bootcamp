"""
retriever.py — Load ChromaDB and expose a retriever for similarity search.
"""

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_DIR = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"


def load_vectorstore() -> Chroma:
    """Load the persisted ChromaDB vector store."""
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name="medical_docs",
    )
    return vectorstore


def get_retriever(k: int = 4):
    """
    Return a LangChain retriever that fetches the top-k most relevant chunks.

    Args:
        k: Number of chunks to retrieve per query (default: 4).
    """
    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
    return retriever


def retrieve_chunks(query: str, k: int = 4) -> list:
    """
    Directly retrieve chunks for a query — useful for inspection/debugging.

    Returns:
        List of Document objects with page_content and metadata.
    """
    retriever = get_retriever(k=k)
    chunks = retriever.invoke(query)
    return chunks


if __name__ == "__main__":
    # Quick test: retrieve chunks for a sample query
    query = "What are the symptoms of type 2 diabetes?"
    print(f"Query: {query}\n")
    chunks = retrieve_chunks(query, k=3)
    for i, chunk in enumerate(chunks, 1):
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", "?")
        print(f"--- Chunk {i} (source: {source}, page: {page}) ---")
        print(chunk.page_content[:300])
        print()